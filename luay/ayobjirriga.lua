require ("declare")
require ("ayobj")
require ("ayutilities")

declare "AyObjIrriga"
AyObjIrriga = inheritsFrom(AyObj)
function AyObjIrriga:new(id, name, type, redisconf, db)
   local o = AyObjIrriga:create()
   local ret = o:init_obj(id, name, type, redisconf, db)
   if (ret ~= '') then
      return ret
   end
   o.obj_sub_list = string.format("irriga.obj.list:%d", o.id)
   o.irriga_id = o:get_full_obj_key(string.format("irriga:%d", o.id))
   o:init_irriga()
   return o
end

function AyObjIrriga:init_irriga()
   self:obj_list_change_begin()
   self.redis:pipeline(function(p)
			  p:hmset(self.irriga_id, "confid", self.id, "objtype", "irriga")
			  p:sadd(self.obj_sub_list, self.irriga_id)
			  p:sadd("obj.list", self.irriga_id)
		       end)
   self:obj_bind(self.irriga_id, 'temp_cameretta', {{'ioi:651648:sg9vGB', 'value'}}, 
		 function(objects)
		    return tonumber(objects['ioi:651648:sg9vGB']['value'])
		 end)
   self:obj_bind(self.irriga_id, 'temp_camera', {{'ioi:651649:sg9vGB', 'value'}}, 
		 function(objects)
		    return tonumber(objects['ioi:651649:sg9vGB']['value'])
		 end)
   self:obj_bind(self.irriga_id, 'temp_sala', {{'ioi:651647:sg9vGB', 'value'}}, 
		 function(objects)
		    return tonumber(objects['ioi:651647:sg9vGB']['value'])
		 end)
   self:obj_bind(self.irriga_id, 'temp_esterna', {{'ioi:651650:sg9vGB', 'value'}}, 
		 function(objects)
		    return tonumber(objects['ioi:651650:sg9vGB']['value'])
		 end)

   self:obj_bind(self.irriga_id, 'stato', {{'ioi:651651:sg9vGB', 'value'}}, 
		 function(objects)
		    local v = tonumber(objects['ioi:651651:sg9vGB']['value'])
		    if (v == 0) then return 'disconnesso' end
		    if (v == 1) then return 'connesso' end
		    if (v == 5) then return 'irrigando' end
		    return v
		 end)

   self:obj_bind(self.irriga_id, 'irriga_data_giorni', {{'ioi:651652:sg9vGB', 'value'}}, 
		 function(objects)
		    return tonumber(objects['ioi:651652:sg9vGB']['value'])
		 end)
   self:obj_bind(self.irriga_id, 'irriga_data_ora', {{'ioi:651653:sg9vGB', 'value'}}, 
		 function(objects)
		    return tonumber(objects['ioi:651653:sg9vGB']['value'])
		 end)
   self:obj_bind(self.irriga_id, 'irriga_data_minuti', {{'ioi:651654:sg9vGB', 'value'}}, 
		 function(objects)
		    return tonumber(objects['ioi:651654:sg9vGB']['value'])
		 end)

   self:obj_bind(self.irriga_id, 'irriga_tempo_giardino', {{'ioi:651655:sg9vGB', 'value'}}, 
		 function(objects)
		    return tonumber(objects['ioi:651655:sg9vGB']['value'])
		 end)
   self:obj_bind(self.irriga_id, 'irriga_tempo_orto', {{'ioi:651656:sg9vGB', 'value'}}, 
		 function(objects)
		    return tonumber(objects['ioi:651656:sg9vGB']['value'])
		 end)

   self:obj_added(self.irriga_id, self.name)
   self:obj_list_change_end()
end

function AyObjIrriga:handle_unload()
   return true
end

function AyObjIrriga:handle_reload(oid)
   return true
end

function AyObjIrriga:handle_sub_event(flat)
end

local objirriga = {ayobjplugin= '1', class=AyObjIrriga}
function objirriga.plugin(r)
   local params = {stato={persist=false, default="", apidesc="", apiformat="*numeric"},
		   temp_sala={persist=false, default="0", apidesc="", apiformat="numeric"},
		   temp_cameretta={persist=false, default="0", apidesc="", apiformat="numeric"},
		   temp_esterna={persist=false, default="0", apidesc="", apiformat="numeric"},
		   temp_camera={persist=false, default="0", apidesc="", apiformat="numeric"},
		   irriga_data_giorni={persist=false, default="0", apidesc="", apiformat="numeric"},
		   irriga_data_ora={persist=false, default="0", apidesc="", apiformat="numeric"},
		   irriga_data_minuti={persist=false, default="0", apidesc="", apiformat="numeric"},
		   irriga_tempo_giardino={persist=false, default="0", apidesc="", apiformat="numeric"},
		   irriga_tempo_orto={persist=false, default="0", apidesc="", apiformat="numeric"},
		   api_desc="Luca irriga object."}

   r:hmset("obj.supported:IRRIGA", "name", "irriga", "type", "irriga", "params", ayut_msgpack_pack(params, true))
   r:sadd("obj.supported.list", "IRRIGA")
   return "IRRIGA"
end
return objirriga
