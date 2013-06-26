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
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ListView;

import com.aylook.aydroid.AyObjectPropAdapter.AyObjectPropHolder;

public class ObjPropActivity extends ListActivity implements AyDroidServiceInterface {
	
	private boolean mIsBound = false;
	private AyDroidService mBoundService;
	AyDroidServiceInterface dsi = this;	
	private AyObject obj;
	
	private ServiceConnection mConnection = new ServiceConnection() {
	    public void onServiceConnected(ComponentName className, IBinder service) {
	        // This is called when the connection with the service has been
	        // established, giving us the service object we can use to
	        // interact with the service.  Because we have bound to a explicit
	        // service that we know is running in our own process, we can
	        // cast its IBinder to a concrete class and directly access it.
	        mBoundService = ((AyDroidService.LocalBinder)service).getService();
	        mBoundService.listenService(dsi);
	    }

	    public void onServiceDisconnected(ComponentName className) {
	        // This is called when the connection with the service has been
	        // unexpectedly disconnected -- that is, its process crashed.
	        // Because it is running in our same process, we should never
	        // see this happen.
	        mBoundService = null;
	    }
	};

	
	void doBindService() {
	    // Establish a connection with the service.  We use an explicit
	    // class name because we want a specific service implementation that
	    // we know will be running in our own process (and thus won't be
	    // supporting component replacement by other applications).
	    bindService(new Intent(this, 
	            AyDroidService.class), mConnection, Context.BIND_AUTO_CREATE);
	    mIsBound = true;
	}

	void doUnbindService() {
	    if (mIsBound) {
	        // Detach our existing connection.
	        unbindService(mConnection);
	        mIsBound = false;
	    }
	}

	public void newObjList(AyObject[] o, String[] ot){
	}
	
	public void newObjProperties(AyObject o){
		if (obj.id.equals(o.id)) {
			ListView lv = getListView();
			obj = o;
			lv.post(new Runnable() {
		        public void run() {
		        	refreshData();
		        }
		      });			
		}
	}
	
	private void refreshData() {
		ListView lv = getListView();
		AyObjectPropAdapter adapter = (AyObjectPropAdapter) lv.getAdapter();
		adapter.clear();
		for (AyObjectProp p: obj.getPropsArray()) {
			adapter.add(p);
		}
	}
		
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        obj = AyDroidSingleton.getObj();
        ArrayList<AyObjectProp> lst = new ArrayList<AyObjectProp>();
        lst.addAll(Arrays.asList(obj.getPropsArray()));
        
        AyObjectPropAdapter adapter = new AyObjectPropAdapter(this,
                R.layout.lv_obj_pro_row_prop, lst);

        doBindService();
        
        ListView lv = getListView();
        lv.setAdapter(adapter);        
        lv.setTextFilterEnabled(true);

        lv.setOnItemClickListener(new OnItemClickListener() {
          public void onItemClick(AdapterView<?> parent, View view,
              int position, long id) {
        	 Log.i("AyDroid", "selected prop" + position);
        	 //open new obj prop intent passing object
          	 AyObjectPropHolder objh = (AyObjectPropHolder) view.getTag();
          	 //AyDroidSingleton.setObj(objh.obj);
          	 Intent intent = new Intent(getApplicationContext(), ObjPropActivity.class);
          	 startActivity(intent);

          }
        });
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
