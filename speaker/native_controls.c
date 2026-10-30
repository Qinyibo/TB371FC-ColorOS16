/* Request/state controls are API 19. Register access is exclusively under
 * the same DSP mutex used by native firmware/profile transitions. */
static DEFINE_SPINLOCK(r94_request_lock);
static unsigned int r94_generation;
static int r94_enable, r94_slots[4] = {0,1,0,1};
/* Per-device: ack, exact route readback, errno, profile epoch, ledger flags. */
static int r94_status[4][5];
static int tb371fc_selector;
static int tb371fc_device_index(struct tfa98xx *t)
{
 static const unsigned char address[] = {0x34,0x37,0x36,0x35};
 int n;
 if (strcmp(fw_name,"tfa98xx_QS.cnt") || t->i2c->adapter->nr != 6 ||
     !t->tfa || t->tfa->rev != 0x1a94) return -1;
 for(n=0;n<4;n++) if(t->i2c->addr==address[n]) return n;
 return -1;
}
static int r94_read(void *p, unsigned char r, unsigned short *v)
{
 struct tfa98xx *t=p; unsigned int value; int ret;
 ret=regmap_read(t->regmap,r,&value);if(!ret)*v=value;return ret;
}
static int r94_write(void *p,unsigned short v)
{
 struct tfa98xx *t=p;
 return regmap_update_bits(t->regmap,0x23,0x00ff,v & 0xff);
}
static int r94_mute(void *p,int on)
{
 struct tfa98xx *t=p;unsigned short power,mute;
 if(on && !t->route_ampc_owned) {
  if(r94_read(t,0,&power))return -EIO;
  t->route_ampc_original=power & 0x40;
  t->route_ampc_owned=1; /* Claim before I/O; failure can reach hardware. */
 }
 /* Relinquish manual ownership while CFSM is still asserted. Native DSP
  * protection/control resumes before its normal unmute sequence. */
 if(!on && t->route_ampc_owned &&
    regmap_update_bits(t->regmap,0,0x40,t->route_ampc_original))return -EIO;
 if(tfa98xx_set_mute(t->tfa,on ? Tfa98xx_Mute_Digital : Tfa98xx_Mute_Off)
    != Tfa98xx_Error_Ok)return -EIO;
 /* With AMPC=1, DSP can keep SWS engaged despite manual AMPE=0. Take
  * manual control only after digital mute and manual AMP-off were set.
  * No DSP bypass, gain, supply, protection, calibration or OTP changes. */
 if(on && regmap_update_bits(t->regmap,0,0x40,0))return -EIO;
 if(r94_read(p,0,&power)||r94_read(p,0x51,&mute))return -EIO;
 if(on)return (!(power & 0x48) && (mute & 8)) ? 0 : -EIO;
 if(!(power&8) || (mute&8) ||
    (t->route_ampc_owned && (power&0x40)!=t->route_ampc_original))return -EIO;
 t->route_ampc_owned=0;return 0;
}
static int r94_wait_quiet(void *p)
{
 unsigned short status; int n;
 /* SWS is the actual TFA9894 amplifier-engaged status, not a fabricated
  * fixed soft-mute ramp duration. No route write until it deasserts. */
 for(n=0;n<50;n++) {
  if(r94_read(p,0x10,&status))return -EIO;
  if(!(status&0x0800))return 0;
  usleep_range(1000,1500);
 }
 return -ETIMEDOUT;
}
static const struct r94_route_ops r94_ops={r94_read,r94_write,r94_mute,r94_wait_quiet};
static enum tfa_error r94_dev_stop(struct tfa98xx *t)
{
 enum tfa_error ret;unsigned short power;
 if(t->route_ledger.mute_owned && r94_release_mute(&t->route_ledger,&r94_ops,t))
  return (enum tfa_error)Tfa98xx_Error_Fail;
 ret=tfa_dev_stop(t->tfa);
 /* Native stop supersedes an attempted transaction mute. A recovery retry
  * must not turn an amplifier back on after playback was stopped. */
 if(ret==tfa_error_ok && !r94_read(t,0,&power) && !(power&8))
  t->route_ledger.mute_owned=0;
 return ret;
}
static void r94_publish(struct tfa98xx *t,int n,unsigned int gen,int ret)
{
 unsigned long flags; unsigned short word=0;
 if(r94_read(t,0x23,&word) && !ret)ret=-EIO;
 spin_lock_irqsave(&r94_request_lock,flags);
 r94_status[n][0]=gen;r94_status[n][1]=word;r94_status[n][2]=ret;
 r94_status[n][3]=t->route_epoch;
 r94_status[n][4]=t->route_ledger.owned | (t->route_ledger.mute_owned<<1);
 spin_unlock_irqrestore(&r94_request_lock,flags);
}
static void tb371fc_rotation_work(struct work_struct *work)
{
 struct tfa98xx *t=container_of(work,struct tfa98xx,rotation_work.work);
 static const int factory[]={0,1,0,1};
 unsigned long flags;unsigned int gen;int on,slot,n,ret;
 const char *name;unsigned short target;
 n=tb371fc_device_index(t);if(n<0)return;
 spin_lock_irqsave(&r94_request_lock,flags);
 gen=r94_generation;on=r94_enable;slot=r94_slots[n];
 spin_unlock_irqrestore(&r94_request_lock,flags);
 if(!gen)return;
 mutex_lock(&t->dsp_lock);
 name=tfa_cont_profile_name(t,t->profile);
 if(on && (!name || strcmp(name,(n==0||n==1)?"voice_nonRotation":"voice2_nonRotation"))) {
  /* Restore only a still-owned generation. A foreign firmware word is
   * refused by the core; a successful profile reload cleared the ledger. */
  ret=r94_route_transaction(&t->route_ledger,&r94_ops,t,0,0);
  if(!ret)ret=-EAGAIN;
 } else if(on && gen<=t->route_floor) ret=-EAGAIN;
 else {
  target=(slot==factory[n]) ? 0x0410 : 0x0401;
  ret=r94_route_transaction(&t->route_ledger,&r94_ops,t,target,on);
 }
 r94_publish(t,n,gen,ret);
 if(on && !ret)t->route_profile=t->profile;
 mutex_unlock(&t->dsp_lock);
 if((ret==-EAGAIN || ret==-EIO) && READ_ONCE(t->rotation_attempts)<4) {
  WRITE_ONCE(t->rotation_attempts,READ_ONCE(t->rotation_attempts)+1);
  mod_delayed_work(t->tfa98xx_wq,&t->rotation_work,msecs_to_jiffies(50));
 }
 if(ret && ret!=-EAGAIN)dev_warn_ratelimited(&t->i2c->dev,"r94 route gen=%u err=%d owned=%d mute=%d\n",gen,ret,t->route_ledger.owned,t->route_ledger.mute_owned);
}
static void r94_profile_reset(struct tfa98xx *t,int profile)
{
 unsigned long flags;unsigned short word;int n=tb371fc_device_index(t);if(n<0)return;
 /* Caller holds DSP lock and native start has successfully installed a
  * fresh configuration. Only a new media request may claim that profile. */
 /* A same-profile volume update need not rewrite slot registers. Retain
  * its ledger unless actual readback proves native restoration or takeover. */
 if(profile!=t->route_profile || (!r94_read(t,0x23,&word) &&
    (word==t->route_ledger.original || (word!=t->route_ledger.last && word!=t->route_ledger.previous))))
  memset(&t->route_ledger,0,sizeof(t->route_ledger));
 t->route_epoch++;
 spin_lock_irqsave(&r94_request_lock,flags);
 t->route_floor=r94_generation;
 r94_status[n][0]=0;r94_status[n][1]=0;r94_status[n][2]=-EAGAIN;
 r94_status[n][3]=t->route_epoch;
 r94_status[n][4]=t->route_ledger.owned | (t->route_ledger.mute_owned<<1);
 spin_unlock_irqrestore(&r94_request_lock,flags);
}
static int tb371fc_rotation_info(struct snd_kcontrol *k,struct snd_ctl_elem_info *i)
{i->type=SNDRV_CTL_ELEM_TYPE_INTEGER;i->count=1;i->value.integer.min=0;i->value.integer.max=7;return 0;}
static int tb371fc_rotation_get(struct snd_kcontrol *k,struct snd_ctl_elem_value *v)
{v->value.integer.value[0]=READ_ONCE(tb371fc_selector);return 0;}
static int tb371fc_rotation_put(struct snd_kcontrol *k,struct snd_ctl_elem_value *v)
{
 int changed;long s=v->value.integer.value[0];if(s<0||s>7)return -EINVAL;
 changed=s!=READ_ONCE(tb371fc_selector);WRITE_ONCE(tb371fc_selector,s);
 /* Original HAL 0..3 is metadata only; it must not race media ownership. */
 return changed;
}
static int r94_request_info(struct snd_kcontrol *k,struct snd_ctl_elem_info *i)
{i->type=SNDRV_CTL_ELEM_TYPE_INTEGER;i->count=5;i->value.integer.min=0;i->value.integer.max=1;return 0;}
static int r94_request_get(struct snd_kcontrol *k,struct snd_ctl_elem_value *v)
{
 unsigned long f;int n;spin_lock_irqsave(&r94_request_lock,f);
 v->value.integer.value[0]=r94_enable;for(n=0;n<4;n++)v->value.integer.value[n+1]=r94_slots[n];
 spin_unlock_irqrestore(&r94_request_lock,f);return 0;
}
static int r94_request_put(struct snd_kcontrol *k,struct snd_ctl_elem_value *v)
{
 struct tfa98xx *t;unsigned long f;int n;
 for(n=0;n<5;n++)if(v->value.integer.value[n]<0||v->value.integer.value[n]>1)return -EINVAL;
 mutex_lock(&tfa98xx_mutex);
 spin_lock_irqsave(&r94_request_lock,f);
 r94_enable=v->value.integer.value[0];for(n=0;n<4;n++)r94_slots[n]=v->value.integer.value[n+1];
 if(++r94_generation>=0x7fffffff)r94_generation=1;
 spin_unlock_irqrestore(&r94_request_lock,f);
 list_for_each_entry(t,&tfa98xx_device_list,list)if(tb371fc_device_index(t)>=0 && t->component) {
  WRITE_ONCE(t->rotation_attempts,0);mod_delayed_work(t->tfa98xx_wq,&t->rotation_work,0);
 }
 mutex_unlock(&tfa98xx_mutex);return 1;
}
static int r94_state_info(struct snd_kcontrol *k,struct snd_ctl_elem_info *i)
{i->type=SNDRV_CTL_ELEM_TYPE_INTEGER;i->count=22;i->value.integer.min=-2147483647;i->value.integer.max=2147483647;return 0;}
static int r94_state_get(struct snd_kcontrol *k,struct snd_ctl_elem_value *v)
{
 unsigned long f;int n,j;spin_lock_irqsave(&r94_request_lock,f);
 v->value.integer.value[0]=19;v->value.integer.value[1]=r94_generation;
 for(n=0;n<4;n++)for(j=0;j<5;j++)v->value.integer.value[2+n*5+j]=r94_status[n][j];
 spin_unlock_irqrestore(&r94_request_lock,f);return 0;
}
