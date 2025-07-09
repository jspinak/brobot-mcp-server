package io.github.jspinak.brobot.cli.models;

import java.util.Map;

/**
 * Result model for action execution.
 */
public class ActionResult {
    private boolean success;
    private String actionType;
    private double duration;
    private String resultState;
    private String error;
    private Map<String, Object> metadata;

    public ActionResult(boolean success, String actionType, double duration) {
        this.success = success;
        this.actionType = actionType;
        this.duration = duration;
    }

    // Getters and setters
    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }
    
    public String getActionType() { return actionType; }
    public void setActionType(String actionType) { this.actionType = actionType; }
    
    public double getDuration() { return duration; }
    public void setDuration(double duration) { this.duration = duration; }
    
    public String getResultState() { return resultState; }
    public void setResultState(String resultState) { this.resultState = resultState; }
    
    public String getError() { return error; }
    public void setError(String error) { this.error = error; }
    
    public Map<String, Object> getMetadata() { return metadata; }
    public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }
}