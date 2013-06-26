package com.aylook.aydroid;

import java.util.ArrayList;

import android.app.Activity;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

public class AyObjectTypesAdapter extends ArrayAdapter<String>{
	Context context;	
	int layoutResourceId;   
	ArrayList<String> data = null;
	   
	public AyObjectTypesAdapter(Context context, int layoutResourceId, ArrayList<String> data) {
		super(context, layoutResourceId, data);
		this.layoutResourceId = layoutResourceId;
		this.context = context;
		this.data = data;
	}

	@Override
	public View getView(int position, View convertView, ViewGroup parent) {
		View row = convertView;
		AyObjectTypeHolder holder = null;
		
		if(row == null)
		{
			LayoutInflater inflater = ((Activity)context).getLayoutInflater();
			row = inflater.inflate(layoutResourceId, parent, false);
			
			holder = new AyObjectTypeHolder();
			holder.txt1 = (TextView)row.findViewById(R.id.obj_row_txt1);          
			row.setTag(holder);
	    }
		else	
		{	
			holder = (AyObjectTypeHolder)row.getTag();
	    }	
		
		String obj = data.get(position);
		holder.txt1.setText(obj);
		
		return row;
	}
	   	
	static class AyObjectTypeHolder
	{
		TextView txt1;
	}
}
