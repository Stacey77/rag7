package com.agi;

import org.drools.core.impl.InternalKnowledgeBase;
import org.drools.core.impl.KnowledgeBaseFactory;
import org.kie.api.KieBase;
import org.kie.api.runtime.KieSession;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Rule Engine Service using Drools
 * Provides rule-based reasoning capabilities
 */
public class RuleEngineService {
    private static final Logger logger = LoggerFactory.getLogger(RuleEngineService.class);
    
    private InternalKnowledgeBase kbase;
    private List<String> rules;
    private Map<String, Object> workingMemory;
    
    public RuleEngineService() {
        this.kbase = KnowledgeBaseFactory.newKnowledgeBase();
        this.rules = new ArrayList<>();
        this.workingMemory = new HashMap<>();
        
        logger.info("Rule Engine Service initialized");
    }
    
    /**
     * Add a rule to the engine
     */
    public void addRule(String ruleName, String ruleDefinition) {
        try {
            rules.add(ruleDefinition);
            logger.debug("Added rule: {}", ruleName);
        } catch (Exception e) {
            logger.error("Error adding rule", e);
            throw new RuntimeException("Failed to add rule", e);
        }
    }
    
    /**
     * Add a fact to working memory
     */
    public void addFact(String key, Object value) {
        workingMemory.put(key, value);
        logger.debug("Added fact: {} = {}", key, value);
    }
    
    /**
     * Get a fact from working memory
     */
    public Object getFact(String key) {
        return workingMemory.get(key);
    }
    
    /**
     * Fire all rules
     */
    public Map<String, Object> fireRules() {
        Map<String, Object> results = new HashMap<>();
        
        try {
            KieSession ksession = kbase.newKieSession();
            
            // Insert facts into session
            for (Map.Entry<String, Object> entry : workingMemory.entrySet()) {
                ksession.insert(entry.getValue());
            }
            
            // Fire all rules
            int firedCount = ksession.fireAllRules();
            results.put("rules_fired", firedCount);
            
            logger.info("Fired {} rules", firedCount);
            
            ksession.dispose();
        } catch (Exception e) {
            logger.error("Error firing rules", e);
            throw new RuntimeException("Failed to fire rules", e);
        }
        
        return results;
    }
    
    /**
     * Evaluate a condition
     */
    public boolean evaluateCondition(String condition) {
        try {
            // Simple evaluation using working memory
            // In production, this would use a proper expression evaluator
            logger.debug("Evaluating condition: {}", condition);
            
            // Placeholder implementation
            return true;
        } catch (Exception e) {
            logger.error("Error evaluating condition", e);
            return false;
        }
    }
    
    /**
     * Get all rules
     */
    public List<String> getRules() {
        return new ArrayList<>(rules);
    }
    
    /**
     * Get working memory contents
     */
    public Map<String, Object> getWorkingMemory() {
        return new HashMap<>(workingMemory);
    }
    
    /**
     * Clear working memory
     */
    public void clearWorkingMemory() {
        workingMemory.clear();
        logger.info("Working memory cleared");
    }
    
    /**
     * Get statistics
     */
    public Map<String, Integer> getStatistics() {
        Map<String, Integer> stats = new HashMap<>();
        stats.put("total_rules", rules.size());
        stats.put("working_memory_size", workingMemory.size());
        
        logger.debug("Rule engine statistics: {}", stats);
        return stats;
    }
}
