package com.aylook.aydroid;

import java.util.ArrayList;

import android.app.Activity;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

public class AyAylookAdapter extends ArrayAdapter<Aylook>{

    Context context;
    int layoutResourceId;   
    ArrayList<Aylook> data = null;
   
    public AyAylookAdapter(Context context, int layoutResourceId, ArrayList<Aylook> data) {
        super(context, layoutResourceId, data);
        this.layoutResourceId = layoutResourceId;
        this.context = context;
        this.data = data;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        View row = convertView;
        AylookHolder holder = null;
       
        if(row == null)
        {
            LayoutInflater inflater = ((Activity)context).getLayoutInflater();
            row = inflater.inflate(layoutResourceId, parent, false);
           
            holder = new AylookHolder();
            holder.txt1 = (TextView)row.findViewById(R.id.ay_row_txt1);          
            holder.txt2 = (TextView)row.findViewById(R.id.ay_row_txt2);
            holder.txt3 = (TextView)row.findViewById(R.id.ay_row_txt3);
            row.setTag(holder);
        }
        else
        {
            holder = (AylookHolder)row.getTag();
        }
       
        Aylook obj = data.get(position);
        holder.txt1.setText(obj.name);
        holder.txt2.setText(obj.ip);
        holder.txt3.setText(obj.user);
        holder.obj = obj;
       
        return row;
    }
   
    static class AylookHolder
    {
    	Aylook obj;
        TextView txt1;
        TextView txt2;
        TextView txt3;
    }
}