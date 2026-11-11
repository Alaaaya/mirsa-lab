#!/usr/bin/env python3
"""APK smoke/UI checks on a disposable emulator, never a physical device."""
import hashlib,json,os,pathlib,re,subprocess,sys,time,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"out"; OUT.mkdir(exist_ok=True)
report={"schema":1,"status":"fail","platform":"android","scope":"emulator-only","deviceVerified":False,"checks":[],"limitations":["A smoke pass only covers configured actions, not all app features.","Only APKs compatible with the x86_64 emulator image can run.","Ephemeral runner is not a security sandbox for hostile code; no production secrets are supplied."]}
package=None
def adb(*args,check=True):
 p=subprocess.run(["adb","-e",*map(str,args)],capture_output=True,timeout=90)
 if check and p.returncode: raise RuntimeError("adb "+str(args[0])+" failed: "+p.stderr.decode(errors="replace"))
 return p.stdout.decode(errors="replace")
def dump(name):
 adb("shell","uiautomator","dump","/sdcard/mirsa-ui.xml")
 data=adb("shell","cat","/sdcard/mirsa-ui.xml")
 (OUT/(name+".xml")).write_text(data)
 return ET.fromstring(data)
def screen(name):
 p=subprocess.run(["adb","-e","exec-out","screencap","-p"],capture_output=True,timeout=30,check=True)
 if not p.stdout.startswith(b"\x89PNG"): raise RuntimeError("invalid screenshot")
 (OUT/(name+".png")).write_bytes(p.stdout)
def alive():
 pid=adb("shell","pidof",package).strip()
 if not pid: raise RuntimeError("app process exited")
 focused=adb("shell","dumpsys","activity","activities")
 (OUT/"activities.log").write_text(focused)
 if not any(package in line for line in focused.splitlines() if "ResumedActivity" in line): raise RuntimeError("app is not foreground")
def validate_steps(steps):
 if not isinstance(steps,list) or len(steps)>40: raise ValueError("steps must be a list of up to 40 actions")
 for s in steps:
  if not isinstance(s,dict): raise ValueError("invalid step")
  if s.get("action")=="tap":
   if not all(type(s.get(k)) is int and 0<=s[k]<=5000 for k in ("x","y")): raise ValueError("invalid tap")
  elif s.get("action") in ("assert","tapText"):
   if not isinstance(s.get("text"),str) or not 0<len(s["text"])<=200: raise ValueError("invalid text")
  elif s.get("action")=="wait":
   if type(s.get("seconds")) not in (int,float) or not 0<=s["seconds"]<=20: raise ValueError("invalid wait")
  elif s.get("action")!="dump": raise ValueError("unsupported action")
try:
 job=pathlib.Path(sys.argv[1]).resolve()
 cfg=json.loads((job/"job.json").read_text())
 apks=list(job.glob("*.apk"))
 if len(apks)!=1: raise ValueError("exactly one root APK required")
 apk=apks[0]
 report["apkSHA256"]=hashlib.sha256(apk.read_bytes()).hexdigest()
 sdk=pathlib.Path(os.environ["ANDROID_HOME"])
 aapt=sorted((sdk/"build-tools").glob("*/aapt"))[-1]
 badging=subprocess.check_output([str(aapt),"dump","badging",str(apk)],text=True)
 (OUT/"apk-info.log").write_text(badging)
 package=re.search(r"^package: name='([^']+)'",badging,re.M).group(1)
 activity=re.search(r"^launchable-activity: name='([^']+)'",badging,re.M).group(1)
 if not re.fullmatch(r"[a-zA-Z0-9_.]+",package) or not re.fullmatch(r"[a-zA-Z0-9_.$]+",activity): raise ValueError("invalid package/activity")
 steps=cfg.get("steps",[]); validate_steps(steps)
 report.update(package=package,activity=activity,api=adb("shell","getprop","ro.build.version.sdk").strip(),abi=adb("shell","getprop","ro.product.cpu.abi").strip())
 adb("logcat","-c")
 (OUT/"install.log").write_text(adb("install","-r",str(apk)))
 report["checks"].append("apk-installed")
 launch=adb("shell","am","start","-W","-n",package+"/"+activity)
 (OUT/"launch.log").write_text(launch)
 if "Error:" in launch or "Status: ok" not in launch: raise RuntimeError("launch rejected")
 time.sleep(5); alive(); screen("00-launch"); dump("00-launch")
 report["checks"].append("launch-foreground-screenshot-ui-dump")
 for i,s in enumerate(steps):
  name=f"{i+1:02d}-{s['action']}"
  if s["action"]=="tap": adb("shell","input","tap",s["x"],s["y"])
  elif s["action"] in ("assert","tapText"):
   tree=dump(name)
   nodes=[n for n in tree.iter("node") if n.get("text")==s["text"] or n.get("content-desc")==s["text"]]
   if not nodes: raise RuntimeError("UI text not found: "+s["text"])
   if s["action"]=="tapText":
    n=nodes[0]
    if n.get("enabled")!="true": raise RuntimeError("target disabled")
    bounds=re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]",n.get("bounds",""))
    if not bounds: raise RuntimeError("no element bounds")
    x,y,x2,y2=map(int,bounds.groups())
    if x2<=x or y2<=y: raise RuntimeError("element not visible")
    adb("shell","input","tap",(x+x2)//2,(y+y2)//2)
  elif s["action"]=="wait": time.sleep(s["seconds"])
  elif s["action"]=="dump": dump(name)
  time.sleep(1); alive(); screen(name); report["checks"].append(name)
 time.sleep(5); alive()
 crash=adb("logcat","-b","crash","-d","-v","threadtime")
 (OUT/"crash.log").write_text(crash)
 # Fresh isolated emulator: any app/native crash is a failure, not an unrelated ignored signal.
 if any(marker in crash for marker in ("FATAL EXCEPTION","Fatal signal","*** *** ***")): raise RuntimeError("crash buffer contains fatal crash")
 logs=adb("logcat","-d","-v","threadtime")
 if re.search(r"ANR in "+re.escape(package)+r"\b",logs): raise RuntimeError("app ANR detected")
 report["checks"].extend(["process-alive-foreground","no-fatal-logcat-crash"])
 report["status"]="pass"
except Exception as e:
 report["error"]=str(e)
finally:
 for name,args in [("logcat.log",("logcat","-d","-v","threadtime")),("crash.log",("logcat","-b","crash","-d","-v","threadtime"))]:
  try: (OUT/name).write_text(adb(*args,check=False))
  except Exception: pass
 try: screen("final"); dump("final")
 except Exception: pass
 (OUT/"result.json").write_text(json.dumps(report,indent=2)); print(json.dumps(report))
sys.exit(0 if report["status"]=="pass" else 1)
