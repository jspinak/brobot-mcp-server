package io.github.jspinak.brobot.cli;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import io.github.jspinak.brobot.cli.models.ActionRequest;
import io.github.jspinak.brobot.cli.models.ActionResult;
import picocli.CommandLine.Command;
import picocli.CommandLine.Parameters;
import picocli.CommandLine.Option;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Callable;

/**
 * Command to execute an action.
 */
@Command(
    name = "execute-action",
    description = "Execute an automation action"
)
public class ExecuteActionCommand implements Callable<Integer> {
    
    @Parameters(index = "0", description = "JSON payload for the action request")
    private String jsonPayload;
    
    @Option(names = {"-p", "--pretty"}, description = "Pretty print JSON output")
    private boolean prettyPrint;

    @Override
    public Integer call() {
        try {
            // Parse the action request
            Gson gson = new Gson();
            ActionRequest request = gson.fromJson(jsonPayload, ActionRequest.class);
            
            // TODO: Replace with actual Brobot action execution
            ActionResult result = executeMockAction(request);
            
            // Convert result to JSON
            Gson outputGson = prettyPrint 
                ? new GsonBuilder().setPrettyPrinting().create()
                : new Gson();
            
            String json = outputGson.toJson(result);
            System.out.println(json);
            
            return 0;
        } catch (Exception e) {
            System.err.println("Error executing action: " + e.getMessage());
            return 1;
        }
    }
    
    /**
     * Execute mock action for testing.
     * TODO: Replace with actual Brobot integration.
     */
    private ActionResult executeMockAction(ActionRequest request) {
        String actionType = request.getActionType();
        Map<String, Object> metadata = new HashMap<>();
        
        ActionResult result;
        
        switch (actionType) {
            case "click":
                result = new ActionResult(true, actionType, 0.523);
                result.setResultState(request.getTargetState() != null ? request.getTargetState() : "unknown");
                metadata.put("click_location", Map.of("x", 640, "y", 480));
                metadata.put("pattern_found", true);
                metadata.put("confidence", 0.92);
                result.setMetadata(metadata);
                break;
                
            case "type":
                result = new ActionResult(true, actionType, 1.234);
                result.setResultState(request.getTargetState());
                String text = request.getParameters() != null ? 
                    (String) request.getParameters().get("text") : "";
                metadata.put("text_entered", text);
                metadata.put("typing_speed", 50);
                result.setMetadata(metadata);
                break;
                
            case "drag":
                result = new ActionResult(true, actionType, 0.876);
                result.setResultState(request.getTargetState());
                metadata.put("start_location", Map.of("x", 100, "y", 100));
                metadata.put("end_location", Map.of("x", 500, "y", 500));
                metadata.put("drag_duration", 0.5);
                result.setMetadata(metadata);
                break;
                
            case "wait":
                result = new ActionResult(true, actionType, 2.5);
                result.setResultState(request.getTargetState());
                metadata.put("wait_condition", "state_change");
                metadata.put("condition_met", true);
                result.setMetadata(metadata);
                break;
                
            default:
                result = new ActionResult(false, actionType, 0.001);
                result.setError("Unknown action type: " + actionType);
                result.setMetadata(metadata);
                break;
        }
        
        return result;
    }
}