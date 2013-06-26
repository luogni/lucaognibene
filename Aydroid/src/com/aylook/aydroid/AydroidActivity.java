package com.aylook.aydroid;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import android.app.ListActivity;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.IBinder;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ListView;

public class AydroidActivity extends ListActivity implements AyDroidServiceInterface {
    /** Called when the activity is first created. */
	
	private boolean mIsBound = false;
	private AyDroidService mBoundService;
	AyDroidServiceInterface dsi = this;
	private Aylook[] ays = new Aylook[0];
	private int AY_ADD_ALOOK_ADD_CODE = 123;
	
	private ServiceConnection mConnection = new ServiceConnection() {
	    public void onServiceConnected(ComponentName className, IBinder service) {
	        mBoundService = ((AyDroidService.LocalBinder)service).getService();
	        mBoundService.listenService(dsi);
	    	Log.i("AyDroid", "aydroid CONNECTED");
	    }

	    public void onServiceDisconnected(ComponentName className) {
	        mBoundService = null;
	    }
	};
	
	void doBindService() {
	    bindService(new Intent(this, 
	            AyDroidService.class), mConnection, Context.BIND_AUTO_CREATE);
	    mIsBound = true;
	}

	void doUnbindService() {
	    if (mIsBound) {
	        unbindService(mConnection);
	        mIsBound = false;
	    }
	}	
	
	public void newObjList(AyObject[] o, String[] ot){
	}

	public void newObjProperties(AyObject o){	
	}
	
	private void loadAylooks() {
		Set<Aylook> aya = new HashSet<Aylook>(); 
		SharedPreferences settings = getPreferences(0);
		Log.i("Aydroid", "load aylooks");
		int numay = settings.getInt("ayNum", 0);
		Log.i("Aydroid", "" + numay);
		for (int i=0;i<numay;i++) {
			String name = settings.getString("ayName" + i, "");
			if (name.equals("")) {
				continue;
			}
			String ip = settings.getString("ayIP" + i, "");
			String user = settings.getString("ayUser" + i, "");
			String hash = settings.getString("ayHash" + i, "");
			aya.add(new Aylook(name, ip, "", user, hash));
		}
		ays = aya.toArray(new Aylook[0]);
	}	
	
	private void addAylook(Aylook a) {
		Log.i("Aydroid", "add aylook");
		SharedPreferences settings = getPreferences(0);
		SharedPreferences.Editor editor = settings.edit();
		int numay = settings.getInt("ayNum", 0);
		editor.putString("ayName"+numay, a.name);
		editor.putString("ayIP"+numay, a.ip);
		editor.putString("ayUser"+numay, a.user);
		editor.putString("ayHash"+numay, a.hash);
		numay ++;
		editor.putInt("ayNum", numay);
		editor.commit();
	}
	
	private void addAylook() {
		Intent intent = new Intent(getBaseContext(),AyAylookAddActivity.class);
        startActivityForResult(intent, AY_ADD_ALOOK_ADD_CODE);	
	}
	
	protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == AY_ADD_ALOOK_ADD_CODE && resultCode == RESULT_OK) {
            //Display the modified values
        	String name = data.getExtras().getString("Name");
        	String ip = data.getExtras().getString("IP");
        	String user = data.getExtras().getString("User");
        	String hash = data.getExtras().getString("Hash");
        	addAylook(new Aylook(name, ip, "", user, hash));
        }
        super.onActivityResult(requestCode, resultCode, data);
    }
	
	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
	    MenuInflater inflater = getMenuInflater();
	    inflater.inflate(R.menu.aylook_menu, menu);
	    return true;
	}
	
	private void refreshData() {
		ListView lv = getListView();
		loadAylooks();		
		AyAylookAdapter adapter = (AyAylookAdapter) lv.getAdapter();
		adapter.clear();
		for (Aylook p: ays) {
			adapter.add(p);
		}
	}		
	
	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
	    switch (item.getItemId()) {
	        case R.id.ay_refresh:
	        	refreshData();
	            return true;
	        case R.id.ay_add:
	        	addAylook();
	            return true;
	        default:
	            return super.onOptionsItemSelected(item);
	    }
	}
	
	private void loadAylookAdapter() {
        ArrayList<Aylook> lst = new ArrayList<Aylook>();
        lst.addAll(Arrays.asList(ays));
		
        AyAylookAdapter adapter = new AyAylookAdapter(this, R.layout.lv_ay_row, lst);
        
        ListView lv = getListView();
        lv.setAdapter(adapter);        
        lv.setTextFilterEnabled(true);
        
        lv.setOnItemClickListener(new OnItemClickListener() {
          public void onItemClick(AdapterView<?> parent, View view,
              int position, long id) {
        	  Log.i("AyDroid", "selected aylook " + ays[position].name);
              
        	  mBoundService.setAylook(ays[position]);
              Intent intent = new Intent(getApplicationContext(), ObjTypeActivity.class);
              startActivity(intent);
          }
        });				
	}

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        doBindService();
        loadAylooks();
        
        loadAylookAdapter();        
    }    
    
    @Override
    public void onDestroy() {
    	super.onDestroy();
    	doUnbindService();
    }
     
    @Override
    public void onStart() {
    	super.onStart();
    	if (mBoundService != null) {
    		mBoundService.listenService(dsi);
    	}
    }
    
    @Override
    public void onStop() {
    	super.onStop();
    	mBoundService.unListenService(dsi);
    }  
}