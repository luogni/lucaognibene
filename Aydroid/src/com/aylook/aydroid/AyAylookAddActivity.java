package com.aylook.aydroid;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.EditText;

public class AyAylookAddActivity extends Activity{
	EditText txtName, txtIP, txtUser, txtPassword;
	
	public String md5(String s) {
	    try {
	        // Create MD5 Hash
	        MessageDigest digest = java.security.MessageDigest.getInstance("MD5");
	        digest.update(s.getBytes());
	        byte messageDigest[] = digest.digest();
	        
	        // Create Hex String
	        StringBuffer hexString = new StringBuffer();
	        for (int i=0; i<messageDigest.length; i++)
	            hexString.append(Integer.toHexString(0xFF & messageDigest[i]));
	        return hexString.toString();
	        
	    } catch (NoSuchAlgorithmException e) {
	        e.printStackTrace();
	    }
	    return "";
	}
	
	private String findHash(String u, String p) {
		return md5(u + ":" + p);
	}
	
	public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.form_add_aylook);
        Button btn = (Button)findViewById(R.id.form_add_ay_ok);
        txtName = (EditText)findViewById(R.id.form_add_ay_name);
        txtIP = (EditText)findViewById(R.id.form_add_ay_ip);
        txtUser = (EditText)findViewById(R.id.form_add_ay_user);
        txtPassword = (EditText)findViewById(R.id.form_add_ay_password);
 
        btn.setOnClickListener(new OnClickListener() {
            public void onClick(View v) {
                Intent intent = getIntent();
                intent.putExtra("Name", txtName.getText().toString());
                intent.putExtra("IP", txtIP.getText().toString());
                intent.putExtra("User", txtUser.getText().toString());
                intent.putExtra("Hash", findHash(txtUser.getText().toString(),
                								 txtPassword.getText().toString()));
                setResult(RESULT_OK, intent);
                finish();
            }
        });
    }
}
