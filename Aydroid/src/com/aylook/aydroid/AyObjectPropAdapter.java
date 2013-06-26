package com.aylook.aydroid;

import java.util.ArrayList;

import android.app.Activity;
import android.content.Context;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

public class AyObjectPropAdapter extends ArrayAdapter<AyObjectProp>{

    Context context;
    int layoutResourceId;   
    ArrayList<AyObjectProp> data = null;
   
    public AyObjectPropAdapter(Context context, int layoutResourceId, ArrayList<AyObjectProp> data) {
        super(context, layoutResourceId, data);
        this.layoutResourceId = layoutResourceId;
        this.context = context;
        this.data = data;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        View row = convertView;
        AyObjectPropHolder holder = null;
       
        if(row == null)
        {
            LayoutInflater inflater = ((Activity)context).getLayoutInflater();
            row = inflater.inflate(layoutResourceId, parent, false);
           
            holder = new AyObjectPropHolder();
            holder.txt1 = (TextView)row.findViewById(R.id.textView1);
            holder.txt2 = (TextView)row.findViewById(R.id.textView2);           
            row.setTag(holder);
        }
        else
        {
            holder = (AyObjectPropHolder)row.getTag();
        }
       
        Log.i("GetView", "" + position);
        AyObjectProp obj = data.get(position);
        Log.i("GetView", obj.name);
        holder.txt1.setText(obj.name);
        holder.txt2.setText(obj.value);
        holder.name = obj.name;
       
        return row;
    }
   
    static class AyObjectPropHolder
    {
        TextView txt1;
        TextView txt2;        
        String name;
    }
}