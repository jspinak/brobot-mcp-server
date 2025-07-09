package io.github.jspinak.brobot.cli.models;

import java.util.Map;

/**
 * Request model for action execution.
 */
public class ActionRequest {
    private String actionType;
    private Map<String, Object> parameters;
    private String targetState;
    private double timeout;

    public ActionRequest() {
        this.timeout = 10.0; // Default timeout
    }

    // Getters and setters
    public String getActionType() { return actionType; }
    public void setActionType(String actionType) { this.actionType = actionType; }
    
    public Map<String, Object> getParameters() { return parameters; }
    public void setParameters(Map<String, Object> parameters) { this.parameters = parameters; }
    
    public String getTargetState() { return targetState; }
    public void setTargetState(String targetState) { this.targetState = targetState; }
    
    public double getTimeout() { return timeout; }
    public void setTimeout(double timeout) { this.timeout = timeout; }
}