package com.aylook.aydroid;

import java.util.Arrays;
import java.util.Comparator;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class AyObject {
	public String name;
	public String id;
	public String objtype;
	public Set<AyObjectProp> props = new HashSet<AyObjectProp>();
	
	@SuppressWarnings("unchecked")
	public AyObject(Object m){
		super();
		Map<String, Object> obj = (Map<String, Object>) m;
		name = (String) obj.get("name");
		id = (String) obj.get("id");
		objtype = (String) obj.get("objtype");
		for (String k: obj.keySet()) {
			if (k.equals("actions") == true) {
				Object arr[] = (Object []) obj.get(k);
				for (Object a: arr) {
					String s = (String) a;
					props.add(new AyObjectProp(s, "action"));
				}
			}else {
				props.add(new AyObjectProp(k, (String) obj.get(k)));
			}
		}
	}
	
	public AyObjectProp[] getPropsArray() {
		AyObjectProp[] ret = props.toArray(new AyObjectProp[0]);
		Arrays.sort(ret, new Comparator<AyObjectProp>() {
		    public int compare(AyObjectProp p1, AyObjectProp p2) {
		        return p1.name.compareTo(p2.name);
		    }
		});
		return ret;
	}
}
