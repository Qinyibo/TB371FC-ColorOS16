// SPDX-License-Identifier: Apache-2.0
// Known-ROM test candidate: default privacy-only gateway; independent backend/store.
#include <android/binder_ibinder.h>
#include <android/binder_parcel.h>
#include <android/binder_status.h>
#include <dlfcn.h>
#include <unistd.h>
#include <cstdio>
#include <mutex>
#include <vector>
#include "../pms_policy.h"

static constexpr char kDescriptor[] = "vendor.oplus.hardware.cryptoeng.ICryptoeng";
static constexpr char kPublic[] = "vendor.oplus.hardware.cryptoeng.ICryptoeng/default";
static constexpr char kBacking[] = "vendor.oplus.hardware.cryptoeng.ICryptoeng/r94prod";
static constexpr char kHash[] = "765136eb397eb5b85ee1e089d8fec72c15e266b3";
static AIBinder* (*check_service)(const char*);
static binder_exception_t (*add_service)(AIBinder*, const char*);
static void (*start_pool)();
static void (*join_pool)();
static bool (*pool_size)(uint32_t);
static AIBinder_Class* cls;
static AIBinder* backing;
static std::mutex backend_mutex;

struct Bytes {
    std::vector<int8_t> data;
    int32_t max;
    static bool allocate(void* opaque, int32_t n, int8_t** dest) {
        auto* b = static_cast<Bytes*>(opaque);
        if (n < 0 || n > b->max) return false;
        b->data.resize(n);
        *dest = n ? b->data.data() : nullptr;
        return true;
    }
    const uint8_t* ptr() const { return reinterpret_cast<const uint8_t*>(data.data()); }
};
static binder_status_t okay(AParcel* out) {
    AStatus* s = AStatus_newOk();
    binder_status_t r = AParcel_writeStatusHeader(out, s);
    AStatus_delete(s);
    return r;
}
// The installed CryptoEngManager catches RemoteException only. Unchecked
// SecurityException/IllegalArgumentException would escape to its callers.
// A nullable result preserves its existing missing-service failure behavior.
// It is NOT a PMS success response and never contains an auth challenge.
static binder_status_t unavailable(AParcel* out) {
    binder_status_t r = okay(out);
    return r == STATUS_OK ? AParcel_writeByteArray(out, nullptr, -1) : r;
}
static void forget_backing() {
    if (backing) AIBinder_decStrong(backing);
    backing = nullptr;
}
static binder_status_t transact(AIBinder*, transaction_code_t code, const AParcel* in, AParcel* out) {
    binder_status_t r;
    // Public interface metadata grants no password operation or hardware claim.
    if (code == 0xffffff) {
        r = okay(out);
        return r == STATUS_OK ? AParcel_writeInt32(out, 1) : r;
    }
    if (code == 0xfffffe) {
        r = okay(out);
        return r == STATUS_OK ? AParcel_writeString(out, kHash, sizeof(kHash)-1) : r;
    }
    if (code != 1) return STATUS_UNKNOWN_TRANSACTION;
    const uid_t uid = AIBinder_getCallingUid();
    if (!r94pms::allowed_uid(uid)) {
        std::fprintf(stderr, "R94_PMS_GATE2 DENY uid=%u\n", uid);
        return unavailable(out);
    }
    Bytes input{{}, int32_t(r94pms::kMaxRequest)};
    if (AParcel_readByteArray(in, &input, Bytes::allocate) != STATUS_OK ||
        AParcel_getDataPosition(in) != AParcel_getDataSize(in)) return unavailable(out);
    uint32_t method = 0;
    if (!r94pms::request(input.ptr(), input.data.size(), &method)) {
        std::fprintf(stderr, "R94_PMS_GATE2 INVALID uid=%u\n", uid);
        return unavailable(out);
    }
    std::lock_guard<std::mutex> guard(backend_mutex);
    if (backing && !AIBinder_isAlive(backing)) forget_backing();
    if (!backing) {
        backing = check_service(kBacking);
        if (backing && !AIBinder_associateClass(backing, cls)) forget_backing();
    }
    if (!backing) return unavailable(out);
    AParcel *q = nullptr, *reply = nullptr;
    r = AIBinder_prepareTransaction(backing, &q);
    if (r == STATUS_OK) r = AParcel_writeByteArray(q, input.data.data(), input.data.size());
    if (r != STATUS_OK) {
        if (q) AParcel_delete(q);
        forget_backing();
        return unavailable(out);
    }
    // Do not retry enrollment/deletion/reset after an ambiguous failure.
    r = AIBinder_transact(backing, 1, &q, &reply, 0);
    if (r != STATUS_OK) {
        if (reply) AParcel_delete(reply);
        forget_backing();
        return unavailable(out);
    }
    AStatus* status = nullptr;
    r = AParcel_readStatusHeader(reply, &status);
    if (r != STATUS_OK || !status || !AStatus_isOk(status)) {
        if (status) AStatus_delete(status);
        AParcel_delete(reply);
        return unavailable(out);
    }
    AStatus_delete(status);
    Bytes output{{}, int32_t(r94pms::kMaxReply)};
    r = AParcel_readByteArray(reply, &output, Bytes::allocate);
    const bool full = AParcel_getDataPosition(reply) == AParcel_getDataSize(reply);
    AParcel_delete(reply);
    if (r != STATUS_OK || !full || !r94pms::response(output.ptr(), output.data.size(), method))
        return unavailable(out);
    // Preserve actual authentication failure status, never log secret bytes.
    std::fprintf(stderr, "R94_PMS_GATE2 RELAY uid=%u method=%u status=%u\n", uid, method,
                 r94pms::be32(output.ptr()+4));
    r = okay(out);
    return r == STATUS_OK ? AParcel_writeByteArray(out, output.data.data(), output.data.size()) : r;
}
template<class T> static bool symbol(void* lib, const char* name, T* out) {
    *out = reinterpret_cast<T>(dlsym(lib, name));
    return *out != nullptr;
}
int main() {
    if (getuid() != 0) return 10;
    void* lib = dlopen("libbinder_ndk.so", RTLD_NOW | RTLD_LOCAL);
    if (!lib || !symbol(lib,"AServiceManager_checkService",&check_service) ||
        !symbol(lib,"AServiceManager_addService",&add_service) ||
        !symbol(lib,"ABinderProcess_startThreadPool",&start_pool) ||
        !symbol(lib,"ABinderProcess_joinThreadPool",&join_pool) ||
        !symbol(lib,"ABinderProcess_setThreadPoolMaxThreadCount",&pool_size)) return 11;
    AIBinder* prior = check_service(kPublic);
    if (prior) { AIBinder_decStrong(prior); return 12; }
    cls = AIBinder_Class_define(kDescriptor, [](void* p)->void*{return p;}, [](void*){}, transact);
    if (!cls) return 13;
    backing = check_service(kBacking);
    if (!backing || !AIBinder_associateClass(backing, cls)) return 14;
    AIBinder* binder = AIBinder_new(cls, nullptr);
    if (!binder || !pool_size(2)) return 15;
    if (add_service(binder, kPublic) != EX_NONE) return 16;
    std::fprintf(stderr, "R94_PMS_GATE2 READY privacy_only_default nullable_failure\n");
    start_pool(); join_pool();
    AIBinder_decStrong(binder);
    return 0;
}
