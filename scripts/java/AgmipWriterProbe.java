import java.io.File;
import java.util.*;
import org.codehaus.jackson.map.ObjectMapper;
import org.agmip.translators.dssat.DssatSoilOutput;
import org.agmip.translators.dssat.DssatXFileOutput;

/** Diagnostic caller of published writers, never runs the DSSAT model. */
public class AgmipWriterProbe {
    static HashMap load(String path) throws Exception {
        return new ObjectMapper().readValue(new File(path), HashMap.class);
    }
    static HashMap adapt(HashMap ace) {
        HashMap exp = (HashMap)((ArrayList)ace.get("experiments")).get(0);
        exp.put("soil", ((ArrayList)ace.get("soils")).get(0));
        exp.put("weather", ((ArrayList)ace.get("weathers")).get(0));
        return exp;
    }
    public static void main(String[] args) throws Exception {
        String[] cases = {"original", "slfc1_corrected_probe", "slfc1_removed_probe",
            "texture_times100_probe", "missing_pldp", "sentinel_pldp",
            "missing_initial_no3", "missing_dul"};
        for (String label : cases) {
            HashMap ace = load(args[0]);
            HashMap soil = (HashMap)((ArrayList)ace.get("soils")).get(0);
            ArrayList<HashMap> layers = (ArrayList<HashMap>)soil.get("soilLayer");
            HashMap exp = adapt(ace);
            ArrayList<HashMap> events = (ArrayList<HashMap>)((Map)exp.get("management")).get("events");
            HashMap planting = events.stream().filter(e -> "planting".equals(e.get("event"))).findFirst().get();
            if (label.equals("slfc1_corrected_probe")) layers.get(5).put("slfc1", "0.204836");
            if (label.equals("slfc1_removed_probe")) for (HashMap layer: layers) layer.remove("slfc1");
            if (label.equals("texture_times100_probe")) for (HashMap layer: layers)
                for (String key: new String[]{"slcly","slsil","slsnd"})
                    layer.put(key, Double.toString(Double.parseDouble((String)layer.get(key))*100));
            if (label.equals("missing_pldp")) planting.remove("pldp");
            if (label.equals("sentinel_pldp")) planting.put("pldp", "-99");
            if (label.equals("missing_initial_no3"))
                ((HashMap)((ArrayList)((Map)exp.get("initial_conditions")).get("soilLayer")).get(0)).remove("icno3");
            if (label.equals("missing_dul")) layers.get(0).remove("sldul");
            File folder = new File(args[1],label); if (!folder.mkdirs()) throw new Exception("Case folder exists");
            // Writers may mutate maps. Each writer gets an independent JSON deep copy.
            ObjectMapper mapper = new ObjectMapper();
            HashMap soilInput = mapper.readValue(mapper.writeValueAsBytes(exp),HashMap.class);
            HashMap xInput = mapper.readValue(mapper.writeValueAsBytes(exp),HashMap.class);
            DssatSoilOutput sw = new DssatSoilOutput(); sw.writeFile(folder.getAbsolutePath(),soilInput);
            DssatXFileOutput xw = new DssatXFileOutput(); xw.writeFile(folder.getAbsolutePath(),xInput);
            if (sw.getOutputFile()==null || !sw.getOutputFile().isFile()) throw new Exception("No soil output: "+label);
            if (xw.getOutputFile()==null || !xw.getOutputFile().isFile()) throw new Exception("No FileX output: "+label);
            System.out.println(label+" SOIL="+sw.getOutputFile().getName()+" FILEX="+xw.getOutputFile().getName());
        }
    }
}
