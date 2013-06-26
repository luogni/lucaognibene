package com.aylook.aydroid;

import java.util.ArrayList;

import android.app.Activity;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

public class AyObjectAdapter extends ArrayAdapter<AyObject>{

    Context context;
    int layoutResourceId;   
    ArrayList<AyObject> data = null;
   
    public AyObjectAdapter(Context context, int layoutResourceId, ArrayList<AyObject> data) {
        super(context, layoutResourceId, data);
        this.layoutResourceId = layoutResourceId;
        this.context = context;
        this.data = data;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        View row = convertView;
        AyObjectHolder holder = null;
       
        if(row == null)
        {
            LayoutInflater inflater = ((Activity)context).getLayoutInflater();
            row = inflater.inflate(layoutResourceId, parent, false);
           
            holder = new AyObjectHolder();
            holder.txt1 = (TextView)row.findViewById(R.id.obj_row_txt1);          
            row.setTag(holder);
        }
        else
        {
            holder = (AyObjectHolder)row.getTag();
        }
       
        AyObject obj = data.get(position);
        holder.txt1.setText(obj.name);
        holder.obj = obj;
       
        return row;
    }
   
    static class AyObjectHolder
    {
    	AyObject obj;
        TextView txt1;
    }
}