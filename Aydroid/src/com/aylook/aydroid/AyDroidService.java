package com.aylook.aydroid;

import java.net.URI;
import java.util.HashSet;
import java.util.Set;

import org.xmlrpc.android.XMLRPCClient;
import org.xmlrpc.android.XMLRPCException;

import android.app.Service;
import android.content.Intent;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;

public class AyDroidService extends Service {

	private Thread th = null;
	private boolean threadRunning = false;
	public AyObject objs[];
	public String objs_types[];
	private AyDroidServiceInterface dsi = null;
	private Aylook aylook = null;

    /**
     * Class for clients to access.  Because we know this service always
     * runs in the same process as its clients, we don't need to deal with
     * IPC.
     */
    public class LocalBinder extends Binder {
        AyDroidService getService() {
            return AyDroidService.this;
        }
    }
    
	private void reloadObjectData() {
		Log.i("AyDroidService", "reloadObjectData");
		if (aylook == null) {
			objs = new AyObject[0];
			objs_types = new String[0];
			return;
		}
		Log.i("AyDroidService", "connecting to " + aylook.ip + aylook.user + aylook.hash);
		try {
	        URI uri = URI.create("http://" + aylook.ip + "/perl/xml-rpc_server.php");
	        XMLRPCClient client = new XMLRPCClient(uri);			
			Object arr[] = (Object []) client.call("ay_object_list", aylook.user, aylook.hash);
			AyObject ret[] = new AyObject[arr.length];
			Set<String> types = new HashSet<String>();
			int i = 0;
			for (Object a: arr) {
				Log.i("AyDroid2", "build object " + i);
				ret[i] = new AyObject(a);
				types.add(ret[i].objtype);
				i ++;
			}
			objs_types = types.toArray(new String[0]);
			objs = ret;
			return ;
		} catch (XMLRPCException e) {
			Log.w("AyDroid", "Error", e);
		}
		objs = new AyObject[0];
		objs_types = new String[0];			
	}	
	
	public void unListenService(AyDroidServiceInterface dsi) {
		Log.i("AyDroidService", "unListenService");
		if (this.dsi == dsi){
			Log.i("AyDroidService", "unlisten equal");
			this.dsi = null;
		}
	}

	public void listenService(AyDroidServiceInterface dsi) {
		Log.i("AyDroidService", "listenService");
		this.dsi = dsi;  
	}
	
	public void setAylook(Aylook a) {
		aylook = a;
	}
	
    @Override
    public void onCreate() {
    	super.onCreate();
    	Log.i("AyDroidService", "onCreate");
    	th = new Thread() {
    		public void run() {
                while(threadRunning){
                	if (dsi != null) {
                		reloadObjectData();                    
                		for (AyObject o: objs) {
                    		dsi.newObjProperties(o);                    	
                		}
                    	dsi.newObjList(objs, objs_types);
                	}
                    try {
						Thread.sleep(2000);
					} catch (InterruptedException e) {
					}                	
                }
            }       		
    	};
    	threadRunning = true;
    	th.start();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.i("AyDroidService", "Received start id " + startId + ": " + intent);
        // We want this service to continue running until it is explicitly
        // stopped, so return sticky.
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
    	super.onDestroy();
    	Log.i("AyDroidService", "onDestroy");
    	threadRunning = false;
    	dsi = null;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return mBinder;
    }

    // This is the object that receives interactions from clients.
    private final IBinder mBinder = new LocalBinder();
}
