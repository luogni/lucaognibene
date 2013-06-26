package com.aylook.aydroid;


import java.util.ArrayList;
import java.util.Arrays;

import android.app.ListActivity;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
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

public class ObjTypeActivity extends ListActivity implements AyDroidServiceInterface {
    /** Called when the activity is first created. */
	
	private boolean mIsBound = false;
	private AyDroidService mBoundService = null;
	AyDroidServiceInterface dsi = this;
	private AyObject[] objs = new AyObject[0];
	private String[] objs_types = new String[0];
	
	private ServiceConnection mConnection = new ServiceConnection() {
	    public void onServiceConnected(ComponentName className, IBinder service) {
	        mBoundService = ((AyDroidService.LocalBinder)service).getService();
	        mBoundService.listenService(dsi);
	        objs_types = mBoundService.objs_types;
	        objs = mBoundService.objs;
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
		Log.i("ObjType", "new obj list");
		ListView lv = getListView();
    	objs = o;
    	objs_types = ot;
		lv.post(new Runnable() {
	        public void run() {
	        	refreshData();
	        }
	      });
	}

	public void newObjProperties(AyObject o){
		
	}
	

	private void refreshData() {
		ListView lv = getListView();
		AyObjectTypesAdapter adapter = (AyObjectTypesAdapter) lv.getAdapter();
		adapter.clear();
		for (String p: objs_types) {
			adapter.add(p);
		}
	}
	
	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
	    MenuInflater inflater = getMenuInflater();
	    inflater.inflate(R.menu.main_menu, menu);
	    return true;
	}
	
	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
	    switch (item.getItemId()) {
	        case R.id.refresh:
	            refreshData();
	            return true;
	        default:
	            return super.onOptionsItemSelected(item);
	    }
	}
	
	private void loadObjectTypesAdapter() {
        ArrayList<String> lst = new ArrayList<String>();
        lst.addAll(Arrays.asList(objs_types));

        AyObjectTypesAdapter adapter = new AyObjectTypesAdapter(this, R.layout.lv_obj_row, lst);
        
        ListView lv = getListView();
        lv.setAdapter(adapter);        
        lv.setTextFilterEnabled(true);
        
        lv.setOnItemClickListener(new OnItemClickListener() {
          public void onItemClick(AdapterView<?> parent, View view,
              int position, long id) {
        	  Log.i("AyDroid", "selected object type " + objs_types[position]);
              
        	  AyDroidSingleton.setObjs(objs);
        	  AyDroidSingleton.setObjType(objs_types[position]);
              Intent intent = new Intent(getApplicationContext(), ObjActivity.class);
              startActivity(intent);
          }
        });				
	}

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);       
        doBindService();
        loadObjectTypesAdapter();        
    }  
    
    @Override
    public void onDestroy() {
    	super.onDestroy();    	
    	doUnbindService();
    }
     
    @Override
    public void onStart() {
    	super.onStart();
    	Log.i("AyDroid", "onStart type activity");    	
    	if (mBoundService != null) {
    		mBoundService.listenService(dsi);
    	}
    }
    
    @Override
    public void onStop() {
    	super.onStop();
    	Log.i("AyDroid", "onStop type activity");
    	mBoundService.unListenService(dsi);
    }    
}
