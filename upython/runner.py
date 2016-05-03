#coding=utf-8
import os
import re
import time
import threading
import subprocess
from optparse import OptionParser
import ucore


def main():
    parse = OptionParser()
    parse.add_option('-f', '--file', dest='listfile', help='case or list to run', action='store')
    parse.add_option('-s', '--serial', dest='serialno', help='which device to run', action='store')
    parse.add_option('-c', '--count', dest='count', help='how many times to run', action='store', default='1')
    parse.add_option('-r', '--reportdir', dest='reportdir', help='where to capture report', action='store', default=".")
    parse.add_option('-j', '--jar', dest='jarpath', help='which jar to run', action='store')
    parse.add_option('-k', '--apk', dest='apkpath', help='if apk should install', action='store')
    (option, args) = parse.parse_args()

    a = ucore.ADB(option.serialno)
    product = a.adbshell('getprop ro.product.name')
    version = a.adbshell('getprop ro.build.description')
    device = option.serialno
    if option.jarpath != None:
        a.push(option.jarpath)
    else:
        ucore.log.debug('no uiautomator package found!')
    if option.apkpath != None:
        apk = option.apkpath
        cmdString = "aapt dump xmltree " + option.apkpath + " AndroidManifest.xml | sed -n \"/package=/p\" | awk -F'\"' '{print $2}'"
        apkPkg = a.runcmd(cmdString)
        print('apkPkg=%s' %apkPkg)
        if a.isAppExists(apkPkg):
            print('The app already exist!')
            cmdString = "dumpsys package " + apkPkg + "| grep versionCode"
            versionCode1=a.adbshell(cmdString).strip().split("=")[1].strip().split(" ")[0]
            print('versionCode1=%s' %versionCode1)
            cmdString = "aapt dump xmltree " + option.apkpath + " AndroidManifest.xml | sed -n \"/versionCode/p\" | awk -F'0x' '{print strtonum(\"0x\"$4)}'"
            versionCode2 = a.runcmd(cmdString)
            print('versionCode2=%s' %versionCode2)
            if versionCode1 > versionCode2:
                print('uninstall %s!'%apkPkg)
                a.adb("uninstall %s"%apkPkg)
                time.sleep(15)
        a.install(option.apkpath, option.jarpath, apkPkg)
    else:
        apk = 'No apk upload'
        apkPkg = 'No apk upload'
        ucore.log.debug('No apk to install!')
    if option.serialno == None:
        raise ucore.AdbException('Error: MUST specify a serial number!')
    count = int(option.count)
    suite = ucore.TestSuite()
    for i in range(count):
        suite.addTestCase(option.listfile)

    runner = ucore.TextRunner(a, option)

    runner.startSuite(suite)
    ucore.HtmlReport(suite.tests, locals())


    """
    try:
        runner.startSuite(suite)
    except:
        #generate html report here
        print 'runner Exception'
        import html
        html.HtmlReport(suite.tests, runner.report_dir)

    """

    print '\nLog Directory: %s \n' %runner.report_dir

if __name__ == '__main__':
    main()
