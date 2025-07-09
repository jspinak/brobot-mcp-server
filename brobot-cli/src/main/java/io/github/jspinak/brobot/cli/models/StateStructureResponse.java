package io.github.jspinak.brobot.cli.models;

import java.util.List;
import java.util.Map;

/**
 * Response model for state structure command.
 */
public class StateStructureResponse {
    private List<StateInfo> states;
    private String currentState;
    private Map<String, Object> metadata;

    public StateStructureResponse(List<StateInfo> states, String currentState, Map<String, Object> metadata) {
        this.states = states;
        this.currentState = currentState;
        this.metadata = metadata;
    }

    // Getters and setters
    public List<StateInfo> getStates() { return states; }
    public void setStates(List<StateInfo> states) { this.states = states; }
    
    public String getCurrentState() { return currentState; }
    public void setCurrentState(String currentState) { this.currentState = currentState; }
    
    public Map<String, Object> getMetadata() { return metadata; }
    public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }
    
    /**
     * State information.
     */
    public static class StateInfo {
        private String name;
        private String description;
        private List<String> images;
        private List<TransitionInfo> transitions;
        private boolean isInitial;
        private boolean isFinal;

        public StateInfo(String name, String description) {
            this.name = name;
            this.description = description;
            this.images = List.of();
            this.transitions = List.of();
            this.isInitial = false;
            this.isFinal = false;
        }

        // Getters and setters
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        
        public List<String> getImages() { return images; }
        public void setImages(List<String> images) { this.images = images; }
        
        public List<TransitionInfo> getTransitions() { return transitions; }
        public void setTransitions(List<TransitionInfo> transitions) { this.transitions = transitions; }
        
        public boolean isInitial() { return isInitial; }
        public void setInitial(boolean initial) { isInitial = initial; }
        
        public boolean isFinal() { return isFinal; }
        public void setFinal(boolean isFinal) { this.isFinal = isFinal; }
    }
    
    /**
     * Transition information.
     */
    public static class TransitionInfo {
        private String fromState;
        private String toState;
        private String action;
        private double probability;

        public TransitionInfo(String fromState, String toState, String action, double probability) {
            this.fromState = fromState;
            this.toState = toState;
            this.action = action;
            this.probability = probability;
        }

        // Getters and setters
        public String getFromState() { return fromState; }
        public void setFromState(String fromState) { this.fromState = fromState; }
        
        public String getToState() { return toState; }
        public void setToState(String toState) { this.toState = toState; }
        
        public String getAction() { return action; }
        public void setAction(String action) { this.action = action; }
        
        public double getProbability() { return probability; }
        public void setProbability(double probability) { this.probability = probability; }
    }
}