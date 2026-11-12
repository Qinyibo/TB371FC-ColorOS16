package com.oplus.otaui.activity;
import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.WindowInsets;
import android.widget.LinearLayout;
import android.widget.TextView;
public final class EntryActivity extends Activity {
 @Override public void onCreate(Bundle state) {
  super.onCreate(state);
  final LinearLayout root=new LinearLayout(this); root.setOrientation(1);
  final int margin=(int)(24*getResources().getDisplayMetrics().density+0.5f);
  root.setPadding(margin,margin,margin,margin);
  root.setOnApplyWindowInsetsListener(new View.OnApplyWindowInsetsListener(){
   @Override public WindowInsets onApplyWindowInsets(View v,WindowInsets insets){
   android.graphics.Insets bars=insets.getInsets(WindowInsets.Type.systemBars());
   v.setPadding(margin+bars.left,margin+bars.top,margin+bars.right,margin+bars.bottom);
   return insets;
  }});
  TextView title=new TextView(this); title.setText("系统更新已停用"); title.setTextSize(25);root.addView(title);
  TextView body=new TextView(this);body.setTextSize(17);body.setPadding(0,margin,0,0);
  body.setText("当前为 TB371FC 适配系统。原厂系统更新已移除，不能在这里检查、下载或安装 OPPO／一加系统。\n\n后续更新请使用本适配包，并按包内说明操作。");root.addView(body);
  setContentView(root);
 }
}
