package com.aylook.aydroid;


public class AyDroidSingleton {
	private AyObject obj;
	private AyObject[] objs;
	private String objtype;
	
	public static String getObjType() {
		return ISTANZA.objtype;
	}

	public static void setObjType(String objtype) {
		ISTANZA.objtype = objtype;
	}
	private final static AyDroidSingleton ISTANZA = new AyDroidSingleton();
	
	private AyDroidSingleton() {
	}
	
	public static AyDroidSingleton getInstance() {
		return ISTANZA;
	}
	
	public static void setObj(AyObject obj) {
		ISTANZA.obj = obj;
	}
	public static AyObject getObj() {
		return ISTANZA.obj;
	}
	public static void setObjs(AyObject[] objs) {
		ISTANZA.objs = objs;
	}
	public static AyObject[] getObjs() {
		return ISTANZA.objs;
	}	
}
