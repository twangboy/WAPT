# -*- coding: utf-8 -*-
from setuphelpers import *
import time
import tempfile
import hashlib

# registry key(s) where WAPT will find how to remove the application(s)
uninstallkey = []

TASK_TEMPLATE="""\
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>%(created_on)s</Date>
    <Author>WAPT</Author>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <StartBoundary>%(run_on)s</StartBoundary>
      <EndBoundary>%(expired_on)s</EndBoundary>
      <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
      <Enabled>true</Enabled>
    </TimeTrigger>
    <BootTrigger>
      <StartBoundary>%(run_on)s</StartBoundary>
      <EndBoundary>%(expired_on)s</EndBoundary>
      <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <DeleteExpiredTaskAfter>PT0S</DeleteExpiredTaskAfter>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>%(cmd)s</Command>
      <Arguments>%(parameters)s</Arguments>
    </Exec>
  </Actions>
</Task>
"""


def sha256_for_file(fname, block_size=2**20):
    f = open(fname,'rb')
    sha256 = hashlib.sha256()
    while True:
        data = f.read(block_size)
        if not data:
            break
        sha256.update(data)
    return sha256.hexdigest()


def download_waptagent(waptagent_path,expected_sha256):
    if WAPT.repositories:
        for r in WAPT.repositories:
            try:
                waptagent_url = "%s/waptagent.exe" % r.repo_url
                print('Trying %s'%waptagent_url)
                print(wget(waptagent_url,waptagent_path))
                wapt_agent_sha256 = sha256_for_file(waptagent_path)
                # eefac39c40fdb2feb4aa920727a43d48817eb4df waptagent.exe
                if expected_sha256 != wapt_agent_sha256:
                    print('Error : bad SHA256 for the downloaded waptagent.exe\n Expected : %s \n Found : %s '%(expected_sha256,wapt_agent_sha256))
                    continue
                return waptagent_url
            except Exception as e:
                print('Error when trying %s: %s'%(r.name,e))
        error('No proper waptagent downloaded')
    error('No repository found for the download of waptagent.exe')


def full_waptagent_install(min_version,at_startup=False):
    # get it from
    waptagent_path = makepath(tempfile.gettempdir(),'waptagent.exe')
    waptdeploy_path = makepath(tempfile.gettempdir(),'waptdeploy.exe')
    if isfile(waptdeploy_path):
        killalltasks('waptdeploy.exe')
        killalltasks('waptagent.exe')
        remove_file(waptdeploy_path)

    filecopyto(makepath('patchs','waptdeploy.exe'),waptdeploy_path)

    expected_sha256 = open('waptagent.sha256','r').read().splitlines()[0].split()[0]
    if isfile('waptagent.exe'):
        filecopyto('waptagent.exe',waptagent_path)
    if not isfile(waptagent_path) or sha256_for_file(waptagent_path) != expected_sha256:
        download_waptagent(waptagent_path,expected_sha256)
    #create_onetime_task('fullwaptupgrade',waptagent_path,'/VERYSILENT',delay_minutes=15)

    if at_startup or isrunning('waptexit.exe'):
        cmd = '%s --hash=%s --waptsetupurl=%s --wait=15 --temporary --force --minversion=%s' %(waptdeploy_path,expected_sha256,waptagent_path,min_version)
        if not at_startup:
            print('waptexit is running, scheduling a one time task at system startup with command %s'%cmd)
        # task at system startup
        try:
            print(run('schtasks /Create /RU SYSTEM /SC ONSTART /TN fullwaptupgrade /TR "%s" /F /V1 /Z' % cmd))
        except:
            # windows xp doesn't support one time startup task /Z nor /F
            run_notfatal('schtasks /Delete /TN fullwaptupgrade /F')
            print(run('schtasks /Create /RU SYSTEM /SC ONSTART /TN fullwaptupgrade /TR "%s"' % cmd))
    else:
        # use embedded waptagent.exe, wait 15 minutes for other tasks to complete.
        print(create_onetime_task('fullwaptupgrade',waptdeploy_path,'--hash=%s --waptsetupurl=%s --wait=15 --temporary --force --minversion=%s'%(expected_sha256,waptagent_path,min_version),delay_minutes=1))
        time.sleep(2)
        run_notfatal('SCHTASKS /Run /TN "fullwaptupgrade"')


def install():
    # if you want to modify the keys depending on environment (win32/win64... params..)
    if installed_softwares('WAPT Server_is1'):
        error('WAPT server installed on this host. Aborting')

    waptexe = os.path.join(WAPT.wapt_base_dir,'wapt-get.exe')
    if os.path.isfile(waptexe):
        installed_wapt_version = get_file_properties(waptexe)['FileVersion']
    else:
        installed_wapt_version = '0.0.0.0'

    # get upgrade package informations
    package_wapt_version = control.version.split('-')

    full_waptagent_install(package_wapt_version)
    print('Setting up upgrade from WAPT version %s to %s. waptagent install planned for %s'%(installed_wapt_version,package_wapt_version,time.ctime(time.time() + 1*60)))


def audit():
    # Comparing installed WAPT agent version and package version
    (package_wapt_version,package_packaging) = control.version.split('-')
    try:
        with open(os.path.join(WAPT.wapt_base_dir,'version-full')) as fver:
            installed_wapt_version = fver.read()
    except:
        installed_wapt_version = '0.0.0.0'

    if Version(installed_wapt_version) < Version(package_wapt_version):
        print('The installed WAPT version and this version of the WAPT agent packages is not corresponding. Maybe it is because of first install, if the warning remains one day after the date of installation, please consider it.')
        return "WARNING"
    else:
        print('The installed WAPT version and this version of the WAPT agent packages is corresponding, all good.')
        return "OK"
