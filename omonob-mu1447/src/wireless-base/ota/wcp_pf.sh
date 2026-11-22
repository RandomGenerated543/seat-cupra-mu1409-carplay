#!/bin/sh
# Wireless CarPlay Maps. Maintainer: omonob. Source date: 2026-08-29.
# wcp_pf.sh -- 运行时给无线 CarPlay 开 pf 端口(不改 /etc/pf.conf,重启即恢复原厂)
#
#   sh wcp_pf.sh on      生成 /etc/pf.conf 的副本,在 uap0 入站总拦截之前插入放行规则并加载
#   sh wcp_pf.sh off     重新加载原厂 /etc/pf.conf
#   sh wcp_pf.sh check   只生成副本并做语法检查(pfctl -n),不加载
#
# 原厂规则 "block in quick on $wlan_if from any to ($wlan_if)" 把手机发到车机的连接全拦了,
# 只放行 22/25010/49152/53 等。我们的端口固定在 wcp_session_wrap.c 里:
#   TCP 5000 控制 / 5001 事件 / 6030 屏幕 / 6031 仪表副屏(type 111);UDP 5020 保活 / 6020 对时 / 6000,6004 主音频 / 6003 辅音频 / 6011 RTCP
# 只放行热点网段(手机),不对外。
# 车机 ksh:不认 set -u、不认 CRLF;没有 awk/sed 可依赖,用 while read 逐行拷贝。

PFCTL=/mnt/app/armle/sbin/pfctl
SRC=/etc/pf.conf
DST=/dev/shmem/wcp_pf.conf
SRCF=/dev/shmem/wcp_pf.src      # on 时用的原厂文件,off 时照它恢复
ANCHOR='block in quick on $wlan_if from any to ($wlan_if)'

# 找出当前生效的是哪份原厂规则。connectionmanager 按上网通路加载 /etc/pf.conf 或
# pf.mlan0/ppp0/ecm0.conf,只有后者带对应接口的 NAT;拿错了文件会把手机的上网 NAT 冲掉
# (11-02 台架:走路由器 mlan0 时我们重载 pf.conf,手机连热点后就上不了网)。
# 判据是前两条 "nat pass on <接口> all tagged WLAN" 的接口:
#   pf.conf: ppp0,ecm0   pf.ppp0.conf: ppp0,en0   pf.mlan0.conf: mlan0   pf.ecm0.conf: ecm0
# 认不出就返回 1,调用方不加载。
detect() {
    i1=; i2=
    $PFCTL -s nat 2>/dev/null > /dev/shmem/wcp_pf.nat
    while read -r w1 w2 w3 w4 w5 w6 w7 rest; do     # nat pass on <if> all tagged WLAN -> ...
        [ "$w1" = nat ] && [ "$w6" = tagged ] && [ "$w7" = WLAN ] || continue
        if [ -z "$i1" ]; then i1=$w4; else i2=$w4; break; fi
    done < /dev/shmem/wcp_pf.nat
    case "$i1,$i2" in
    mlan0,*)  SRC=/etc/pf.mlan0.conf ;;
    ecm0,*)   SRC=/etc/pf.ecm0.conf ;;
    ppp0,ecm0) SRC=/etc/pf.conf ;;
    ppp0,en0) SRC=/etc/pf.ppp0.conf ;;
    *) echo "认不出当前 pf 规则(NAT 接口 '$i1','$i2'),不加载"; return 1 ;;
    esac
    echo "当前原厂规则 $SRC"
    return 0
}

gen() {
    [ -f $SRC ] || { echo "缺 $SRC"; return 1; }
    n=0
    : > $DST
    while IFS= read -r line; do
        if [ "$line" = "$ANCHOR" ]; then
            echo '# wcp: 无线 CarPlay(wcp_pf.sh 运行时插入)' >> $DST
            echo 'pass in quick on $wlan_if proto tcp from ($wlan_if:network) to ($wlan_if) port { 5000, 5001, 6030, 6031 } keep state allow-opts' >> $DST
            echo 'pass in quick on $wlan_if proto udp from ($wlan_if:network) to ($wlan_if) port { 5020, 6000, 6003, 6004, 6011, 6020 } keep state allow-opts' >> $DST
            n=1
        fi
        echo "$line" >> $DST
    done < $SRC
    [ $n = 1 ] || { echo "没找到 uap0 总拦截规则,/etc/pf.conf 与原厂不同,不加载"; return 1; }
    return 0
}

case "$1" in
on)
    if [ -f $SRCF ]; then
        SRC=`cat $SRCF`; echo "已加载过,沿用 $SRC"   # 我们的规则在生效时 NAT 仍是原厂的,但别再猜一次
    else
        detect || exit 1
    fi
    gen || exit 1
    $PFCTL -n -f $DST || { echo "语法检查失败,不加载"; exit 1; }
    echo $SRC > $SRCF
    $PFCTL -f $DST && echo "已加载 $DST(基于 $SRC)" ;;
off)
    [ -f $SRCF ] && SRC=`cat $SRCF`
    $PFCTL -f $SRC && { rm -f $SRCF; echo "已恢复 $SRC"; } ;;
check)
    detect || exit 1
    gen || exit 1
    $PFCTL -n -f $DST && echo "语法检查通过 $DST" ;;
*)
    echo "用法: sh $0 on|off|check"; exit 1 ;;
esac
