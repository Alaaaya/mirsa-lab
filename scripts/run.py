#!/usr/bin/env python3
import json, os, pathlib, platform, shutil, subprocess, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"out"; OUT.mkdir(exist_ok=True)
report={"schema":1,"status":"fail","scope":"simulator-only","deviceVerified":False,"target":None,"checks":[],"limitations":["Encrypted App Store IPAs (including TikTok) and device-only dylibs cannot run on the iOS simulator.","Sample pass does not validate hooks in a different real app.","Runner is ephemeral but not a security sandbox for hostile native code. No production credentials are supplied."]}
def run(args, name, **kw):
 with (OUT/(name+".log")).open("w") as f:
  p=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=kw.pop("timeout",600),**kw)
 if p.returncode: raise RuntimeError(name+" failed; inspect "+name+".log")
 return p
try:
 job=pathlib.Path(sys.argv[1]).resolve()
 cfg=json.loads((job/"job.json").read_text())
 report["target"]=cfg.get("target","sample")
 if report["target"] not in ("sample","source"): raise ValueError("target must be sample or source; device IPA/encrypted IPA unsupported")
 # Only data and source are accepted, never scripts or an untrusted Xcode project.
 if report["target"]=="source":
  shutil.rmtree(ROOT/"Host"); shutil.copytree(job/"app-source",ROOT/"Host",symlinks=False)
 sdk=subprocess.check_output(["xcrun","--sdk","iphonesimulator","--show-sdk-path"],text=True).strip()
 arch=platform.machine()
 dylib=ROOT/"Host"/"Tweak.dylib"
 source=job/"tweak.m"
 if source.exists():
  run(["xcrun","clang","-dynamiclib","-fobjc-arc","-arch",arch,"-isysroot",sdk,"-mios-simulator-version-min=16.0","-framework","UIKit","-framework","Foundation",str(source),"-o",str(dylib)],"compile")
 else:
  shutil.copy2(job/"tweak.dylib",dylib)
  run(["xcrun","vtool","-show-build",str(dylib)],"binary-platform")
  if "IOSSIMULATOR" not in (OUT/"binary-platform.log").read_text(): raise ValueError("dylib is not an iOS simulator binary")
 run(["lipo","-verify_arch",arch,str(dylib)],"architecture")
 # Test resources are constants, not executable test code supplied by the job.
 checks=json.loads((job/"checks.json").read_text())
 required={"open","panel","close","gesture","gestureValue"}
 if set(checks)!=required or not all(isinstance(x,str) and 0<len(x)<200 for x in checks.values()): raise ValueError("invalid checks.json")
 (ROOT/"Tests"/"checks.json").write_text(json.dumps(checks))
 run(["xcodegen","generate"],"generate",cwd=ROOT)
 devices=json.loads(subprocess.check_output(["xcrun","simctl","list","devices","available","-j"]))
 available=[d for key,ds in devices["devices"].items() if "iOS" in key for d in ds if "iPhone" in d["name"]]
 if not available: raise RuntimeError("no iPhone simulator available")
 device=available[0]["udid"]; report["simulator"]=available[0]
 base=["xcodebuild","-project","MirsaLab.xcodeproj","-scheme","Lab","-destination","platform=iOS Simulator,id="+device,"-derivedDataPath","build","CODE_SIGNING_ALLOWED=NO"]
 run(base+["build-for-testing"],"build",cwd=ROOT,timeout=900)
 app=ROOT/"build/Build/Products/Debug-iphonesimulator/LabHost.app"
 # Ensure exact generated dylib is bundled and signed only with ad hoc simulator identity.
 shutil.copy2(dylib,app/"Tweak.dylib")
 run(["codesign","--force","--sign","-",str(app/"Tweak.dylib")],"sign-dylib")
 run(["codesign","--force","--deep","--sign","-",str(app)],"sign-host")
 run(base+["test-without-building","-parallel-testing-enabled","NO","-resultBundlePath",str(OUT/"Lab.xcresult")],"ui",cwd=ROOT,timeout=900)
 report["checks"]=["launch-with-dlopen","button-visible-and-hittable","menu-open","menu-close","menu-reopen-reset","double-tap-real-element-and-effect","foreground-after-interaction"]
 report["status"]="pass"
except Exception as e:
 report["error"]=str(e)
finally:
 # Collect diagnostics on success AND failure. Missing diagnostics never becomes a fake pass.
 subprocess.run(["xcrun","simctl","io","booted","screenshot",str(OUT/"final.png")],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 with (OUT/"console.log").open("w") as f:
  subprocess.run(["xcrun","simctl","spawn","booted","log","show","--last","15m","--style","compact","--predicate",'process == "LabHost" OR eventMessage CONTAINS "MIRSA"'],stdout=f,stderr=subprocess.STDOUT,timeout=90)
 crashes=OUT/"crashes"; crashes.mkdir(exist_ok=True)
 for base in [pathlib.Path.home()/"Library/Logs/DiagnosticReports",pathlib.Path.home()/"Library/Developer/CoreSimulator/Devices"]:
  if base.exists():
   for p in base.rglob("*.ips"):
    if "LabHost" in p.name:
     try: shutil.copy2(p,crashes/p.name)
     except OSError: pass
 if (OUT/"Lab.xcresult").exists():
  subprocess.run(["xcrun","xcresulttool","export","attachments","--path",str(OUT/"Lab.xcresult"),"--output-path",str(OUT/"screenshots")],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=90)
 (OUT/"result.json").write_text(json.dumps(report,indent=2))
 print(json.dumps(report))
sys.exit(0 if report["status"]=="pass" else 1)
