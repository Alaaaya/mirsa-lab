#import <UIKit/UIKit.h>
#import <dlfcn.h>
@interface LabViewController : UIViewController @end
@implementation LabViewController
- (void)viewDidLoad {
 [super viewDidLoad]; self.view.backgroundColor=UIColor.systemBackgroundColor;
 UILabel *label=[[UILabel alloc] initWithFrame:CGRectMake(32,120,320,60)];
 label.text=@"MIRSA / TEST LAB"; label.font=[UIFont monospacedSystemFontOfSize:24 weight:UIFontWeightBold];
 [self.view addSubview:label];
}
@end
@interface LabDelegate : UIResponder <UIApplicationDelegate>
@property(nonatomic,strong) UIWindow *window;
@end
@implementation LabDelegate
- (BOOL)application:(UIApplication*)app didFinishLaunchingWithOptions:(NSDictionary*)options {
 NSString *path=[NSBundle.mainBundle pathForResource:@"Tweak" ofType:@"dylib"];
 if(!dlopen(path.UTF8String,RTLD_NOW|RTLD_GLOBAL)) { NSLog(@"MIRSA_DLOPEN_FAILED %s",dlerror()); abort(); }
 NSLog(@"MIRSA_DLOPEN_OK");
 self.window=[[UIWindow alloc] initWithFrame:UIScreen.mainScreen.bounds];
 self.window.rootViewController=[LabViewController new]; [self.window makeKeyAndVisible]; return YES;
}
@end
int main(int argc,char **argv) { @autoreleasepool { return UIApplicationMain(argc,argv,nil,NSStringFromClass(LabDelegate.class)); } }
