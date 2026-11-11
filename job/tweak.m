#import <UIKit/UIKit.h>
#import <objc/runtime.h>
@interface UIViewController (MirsaLab)
- (void)mirsa_viewDidAppear:(BOOL)animated;
- (void)mirsa_open;
- (void)mirsa_close;
- (void)mirsa_gesture;
@end
@implementation UIViewController (MirsaLab)
- (void)mirsa_viewDidAppear:(BOOL)animated {
 [self mirsa_viewDidAppear:animated];
 if(![NSStringFromClass(self.class) isEqual:@"LabViewController"] || [self.view viewWithTag:912]) return;
 UIButton *button=[UIButton buttonWithType:UIButtonTypeSystem]; button.frame=CGRectMake(32,220,300,64); button.tag=912;
 [button setTitle:@"Open tweak menu" forState:UIControlStateNormal]; button.accessibilityIdentifier=@"tweak.menu";
 [button addTarget:self action:@selector(mirsa_open) forControlEvents:UIControlEventTouchUpInside]; [self.view addSubview:button];
 UILabel *video=[[UILabel alloc] initWithFrame:CGRectMake(32,340,300,140)]; video.text=@"Visible video · double tap"; video.userInteractionEnabled=YES; video.accessibilityIdentifier=@"visible.video";
 UITapGestureRecognizer *tap=[[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(mirsa_gesture)]; tap.numberOfTapsRequired=2; [video addGestureRecognizer:tap]; [self.view addSubview:video];
}
- (void)mirsa_open {
 if([self.view viewWithTag:913]) return;
 UIView *menu=[[UIView alloc] initWithFrame:CGRectMake(32,500,300,160)]; menu.tag=913; menu.backgroundColor=UIColor.secondarySystemBackgroundColor; menu.accessibilityIdentifier=@"tweak.panel";
 UIButton *close=[UIButton buttonWithType:UIButtonTypeSystem]; close.frame=CGRectMake(0,20,300,80); close.accessibilityIdentifier=@"tweak.close"; [close setTitle:@"Close menu" forState:UIControlStateNormal]; [close addTarget:self action:@selector(mirsa_close) forControlEvents:UIControlEventTouchUpInside]; [menu addSubview:close]; [self.view addSubview:menu];
}
- (void)mirsa_close { [[self.view viewWithTag:913] removeFromSuperview]; }
- (void)mirsa_gesture { UILabel *label=(UILabel*)[self.view.subviews filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"accessibilityIdentifier == %@",@"visible.video"]].firstObject; label.text=@"Gesture reached visible video"; label.accessibilityValue=@"gesture.ok"; }
@end
__attribute__((constructor)) static void inject(void) {
 method_exchangeImplementations(class_getInstanceMethod(UIViewController.class,@selector(viewDidAppear:)),class_getInstanceMethod(UIViewController.class,@selector(mirsa_viewDidAppear:)));
 NSLog(@"MIRSA_SAMPLE_INJECTED");
}
