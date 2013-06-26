package com.aylook.aydroid;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashSet;
import java.util.Set;

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

import com.aylook.aydroid.AyObjectAdapter.AyObjectHolder;

public class ObjActivity extends ListActivity implements AyDroidServiceInterface {
	private AyObject objs[];
	private boolean mIsBound = false;
	private AyDroidService mBoundService;
	AyDroidServiceInterface dsi = this;	
	
	private ServiceConnection mConnection = new ServiceConnection() {
	    public void onServiceConnected(ComponentName className, IBinder service) {
	        mBoundService = ((AyDroidService.LocalBinder)service).getService();
	        mBoundService.listenService(dsi);	        
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
	        // Detach our existing connection.
	        unbindService(mConnection);
	        mIsBound = false;
	    }
	}	
	
	public void newObjList(AyObject[] o, String[] ot){
		ListView lv = getListView();
        objs = filterObjectData(o, AyDroidSingleton.getObjType());
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
		AyObjectAdapter adapter = (AyObjectAdapter) lv.getAdapter();
		adapter.clear();
		for (AyObject p: objs) {
			adapter.add(p);
		}
	}		
	
	private void loadObjectAdapter() {
        ArrayList<AyObject> lst = new ArrayList<AyObject>();
        lst.addAll(Arrays.asList(objs));

        AyObjectAdapter adapter = new AyObjectAdapter(this, R.layout.lv_obj_row, lst);
        
        ListView lv = getListView();
        lv.setAdapter(adapter);        
        lv.setTextFilterEnabled(true);
        
        lv.setOnItemClickListener(new OnItemClickListener() {
          public void onItemClick(AdapterView<?> parent, View view,
              int position, long id) {
        	  Log.i("AyDroid", "selected object" + position);
            //open new obj prop intent passing object
        	AyObjectHolder objh = (AyObjectHolder) view.getTag();
            AyDroidSingleton.setObj(objh.obj);
            Intent intent = new Intent(getApplicationContext(), ObjPropActivity.class);
            startActivity(intent);
          }
        });				
	}
    	
	private AyObject[] filterObjectData(AyObject[] oo, String objtype) {
		Set<AyObject> ob = new HashSet<AyObject>();
		AyObject[] ret;
		for (AyObject o: oo) {
			if (o.objtype.equals(objtype)) {
				ob.add(o);
			}
		}		
		ret = ob.toArray(new AyObject[0]);
		Arrays.sort(ret, new Comparator<AyObject>() {
			public int compare(AyObject p1, AyObject p2) {
				return p1.name.compareTo(p2.name);
			}
		});
		return ret;
	}
	
	@Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        doBindService();
        objs = filterObjectData(AyDroidSingleton.getObjs(), AyDroidSingleton.getObjType());        
        loadObjectAdapter();
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
