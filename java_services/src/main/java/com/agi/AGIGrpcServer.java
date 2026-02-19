package com.agi;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

/**
 * gRPC Server for Python-Java communication
 * Exposes AGI Java services to Python components
 */
public class AGIGrpcServer {
    private static final Logger logger = LoggerFactory.getLogger(AGIGrpcServer.class);
    
    private Server server;
    private final int port;
    private final KnowledgeGraphService kgService;
    private final RuleEngineService ruleService;
    
    public AGIGrpcServer(int port, KnowledgeGraphService kgService, RuleEngineService ruleService) {
        this.port = port;
        this.kgService = kgService;
        this.ruleService = ruleService;
    }
    
    /**
     * Start the gRPC server
     */
    public void start() throws IOException {
        server = ServerBuilder.forPort(port)
            .addService(new AGIServiceImpl(kgService, ruleService))
            .build()
            .start();
        
        logger.info("gRPC Server started, listening on port {}", port);
        
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            logger.info("Shutting down gRPC server");
            try {
                AGIGrpcServer.this.stop();
            } catch (InterruptedException e) {
                logger.error("Error during shutdown", e);
            }
        }));
    }
    
    /**
     * Stop the gRPC server
     */
    public void stop() throws InterruptedException {
        if (server != null) {
            server.shutdown().awaitTermination(30, TimeUnit.SECONDS);
            logger.info("gRPC Server stopped");
        }
    }
    
    /**
     * Wait for server termination
     */
    public void blockUntilShutdown() throws InterruptedException {
        if (server != null) {
            server.awaitTermination();
        }
    }
    
    /**
     * gRPC service implementation
     * Note: This is a placeholder. In production, you would generate this from .proto files
     */
    private static class AGIServiceImpl {
        private final KnowledgeGraphService kgService;
        private final RuleEngineService ruleService;
        
        public AGIServiceImpl(KnowledgeGraphService kgService, RuleEngineService ruleService) {
            this.kgService = kgService;
            this.ruleService = ruleService;
        }
        
        // Service methods would be implemented here based on .proto definitions
        // For example:
        // - AddTriple
        // - QueryKnowledgeGraph
        // - AddRule
        // - FireRules
    }
}
