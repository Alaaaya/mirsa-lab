package dev.mirsa.lab.sample;
import android.app.Activity;
import android.os.Bundle;
import android.widget.*;
public class MainActivity extends Activity {
 public void onCreate(Bundle b) {
  super.onCreate(b);
  final LinearLayout root=new LinearLayout(this); root.setOrientation(1); root.setPadding(32,64,32,32);
  TextView title=new TextView(this); title.setText("MIRSA ANDROID LAB"); title.setTextSize(24); root.addView(title);
  Button open=new Button(this); open.setText("Open menu"); root.addView(open);
  final TextView state=new TextView(this); state.setText("Ready"); root.addView(state);
  final LinearLayout panel=new LinearLayout(this); panel.setOrientation(1);
  TextView label=new TextView(this); label.setText("Menu is open"); panel.addView(label);
  Button close=new Button(this); close.setText("Close menu"); panel.addView(close);
  open.setOnClickListener(new android.view.View.OnClickListener(){ public void onClick(android.view.View v){ if(panel.getParent()==null) root.addView(panel); state.setText("Menu opened"); }});
  close.setOnClickListener(new android.view.View.OnClickListener(){ public void onClick(android.view.View v){root.removeView(panel);state.setText("Menu closed");}});
  setContentView(root);
 }
}
