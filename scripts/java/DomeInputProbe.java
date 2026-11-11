import java.io.File;
import java.util.*;
import org.codehaus.jackson.map.ObjectMapper;
import org.agmip.dome.Engine;
import org.agmip.translators.dssat.DssatSoilOutput;
import org.agmip.translators.dssat.DssatXFileOutput;
import org.agmip.translators.dssat.DssatWeatherOutput;

/** Real DOME engine on owned clones; export invoked separately after Python guard. */
public class DomeInputProbe {
    static ObjectMapper mapper = new ObjectMapper();
    static HashMap load(String file) throws Exception {return mapper.readValue(new File(file),HashMap.class);}
    static HashMap cloneMap(HashMap data) throws Exception {return mapper.readValue(mapper.writeValueAsBytes(data),HashMap.class);}
    static HashMap adapt(HashMap ace) {
        HashMap exp=(HashMap)((ArrayList)ace.get("experiments")).get(0);
        exp.put("soil",((ArrayList)ace.get("soils")).get(0));
        exp.put("weather",((ArrayList)ace.get("weathers")).get(0));return exp;
    }
    public static void main(String[] args) throws Exception {
        if (args[0].equals("export")) {
            HashMap exp=load(args[1]);File out=new File(args[2]);if(!out.mkdirs())throw new Exception("Exists");
            DssatSoilOutput s=new DssatSoilOutput();s.writeFile(out.getAbsolutePath(),cloneMap(exp));
            DssatXFileOutput x=new DssatXFileOutput();x.writeFile(out.getAbsolutePath(),cloneMap(exp));
            DssatWeatherOutput w=new DssatWeatherOutput();w.writeFile(out.getAbsolutePath(),cloneMap(exp));
            if(s.getOutputFile()==null || !s.getOutputFile().isFile() || x.getOutputFile()==null || !x.getOutputFile().isFile())throw new Exception("Missing output");
            if(w.getOutputFile()==null || !w.getOutputFile().isFile())throw new Exception("Missing weather output");
            return;
        }
        HashMap all=load(args[2]);HashMap dome=(HashMap)all.values().iterator().next();
        File out=new File(args[3]);if(!out.mkdirs())throw new Exception("Exists");
        for(String label:new String[]{"rules","generators","existing_values","missing_endat"}) {
            HashMap exp=adapt(load(args[1]));
            if(label.equals("missing_endat"))exp.remove("endat");
            if(label.equals("existing_values")) {
                exp.put("sdat","20080101");((HashMap)exp.get("soil")).put("slpf","0.77");
                for(Object o:(ArrayList)((HashMap)exp.get("management")).get("events")) {
                    HashMap e=(HashMap)o;if("fertilizer".equals(e.get("event"))){e.put("fedep","9");break;}
                }
            }
            Engine engine=new Engine(cloneMap(dome),label.equals("generators"));
            if(label.equals("rules"))mapper.writeValue(new File(out,"engine_name.json"),engine.getDomeName());
            if(label.equals("generators")) {
                ArrayList<HashMap<String,Object>> result=engine.applyStg(exp);
                if(result.size()!=1)throw new Exception("Unexpected generated count");exp=result.get(0);
            } else engine.apply(exp);
            mapper.writeValue(new File(out,label+".json"),exp);
        }
    }
}
