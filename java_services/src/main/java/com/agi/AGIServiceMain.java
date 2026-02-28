package com.agi;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Main entry point for AGI Java Services
 * Provides symbolic reasoning capabilities using Apache Jena and Drools
 */
public class AGIServiceMain {
    private static final Logger logger = LoggerFactory.getLogger(AGIServiceMain.class);
    
    public static void main(String[] args) {
        logger.info("Starting AGI Java Services...");
        
        try {
            // Initialize knowledge graph service
            KnowledgeGraphService kgService = new KnowledgeGraphService();
            logger.info("Knowledge Graph Service initialized");
            
            // Initialize rule engine service
            RuleEngineService ruleService = new RuleEngineService();
            logger.info("Rule Engine Service initialized");
            
            // Start gRPC server for Python-Java communication
            AGIGrpcServer server = new AGIGrpcServer(50051, kgService, ruleService);
            server.start();
            logger.info("gRPC Server started on port 50051");
            
            // Wait for termination
            server.blockUntilShutdown();
            
        } catch (Exception e) {
            logger.error("Error starting AGI Java Services", e);
            System.exit(1);
        }
    }
}
