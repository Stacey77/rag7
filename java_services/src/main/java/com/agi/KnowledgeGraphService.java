package com.agi;

import org.apache.jena.rdf.model.*;
import org.apache.jena.vocabulary.RDF;
import org.apache.jena.vocabulary.RDFS;
import org.apache.jena.query.*;
import org.apache.jena.reasoner.Reasoner;
import org.apache.jena.reasoner.ReasonerRegistry;
import org.apache.jena.reasoner.rulesys.GenericRuleReasoner;
import org.apache.jena.reasoner.rulesys.Rule;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Knowledge Graph Service using Apache Jena
 * Provides RDF-based knowledge representation and SPARQL querying
 */
public class KnowledgeGraphService {
    private static final Logger logger = LoggerFactory.getLogger(KnowledgeGraphService.class);
    
    private Model model;
    private InfModel infModel;
    private Reasoner reasoner;
    private String namespace = "http://agi.system/ontology#";
    
    public KnowledgeGraphService() {
        // Create empty model
        this.model = ModelFactory.createDefaultModel();
        this.model.setNsPrefix("agi", namespace);
        
        // Initialize OWL reasoner
        this.reasoner = ReasonerRegistry.getOWLReasoner();
        this.infModel = ModelFactory.createInfModel(reasoner, model);
        
        logger.info("Knowledge Graph Service initialized with OWL reasoner");
    }
    
    /**
     * Add a triple to the knowledge graph
     */
    public void addTriple(String subject, String predicate, String object) {
        try {
            Resource subjectRes = model.createResource(namespace + subject);
            Property predicateProp = model.createProperty(namespace + predicate);
            Resource objectRes = model.createResource(namespace + object);
            
            model.add(subjectRes, predicateProp, objectRes);
            
            // Refresh inference model
            infModel = ModelFactory.createInfModel(reasoner, model);
            
            logger.debug("Added triple: {} --[{}]--> {}", subject, predicate, object);
        } catch (Exception e) {
            logger.error("Error adding triple", e);
            throw new RuntimeException("Failed to add triple", e);
        }
    }
    
    /**
     * Add a literal property
     */
    public void addLiteral(String subject, String predicate, String literalValue) {
        try {
            Resource subjectRes = model.createResource(namespace + subject);
            Property predicateProp = model.createProperty(namespace + predicate);
            
            model.add(subjectRes, predicateProp, literalValue);
            
            infModel = ModelFactory.createInfModel(reasoner, model);
            
            logger.debug("Added literal: {} --[{}]--> '{}'", subject, predicate, literalValue);
        } catch (Exception e) {
            logger.error("Error adding literal", e);
            throw new RuntimeException("Failed to add literal", e);
        }
    }
    
    /**
     * Query knowledge graph using SPARQL
     */
    public List<Map<String, String>> querySparql(String sparqlQuery) {
        List<Map<String, String>> results = new ArrayList<>();
        
        try {
            Query query = QueryFactory.create(sparqlQuery);
            
            try (QueryExecution qexec = QueryExecutionFactory.create(query, infModel)) {
                ResultSet resultSet = qexec.execSelect();
                
                while (resultSet.hasNext()) {
                    QuerySolution solution = resultSet.nextSolution();
                    Map<String, String> row = new HashMap<>();
                    
                    // Extract all variables from solution
                    solution.varNames().forEachRemaining(varName -> {
                        RDFNode node = solution.get(varName);
                        if (node != null) {
                            row.put(varName, node.toString());
                        }
                    });
                    
                    results.add(row);
                }
            }
            
            logger.debug("SPARQL query returned {} results", results.size());
        } catch (Exception e) {
            logger.error("Error executing SPARQL query", e);
            throw new RuntimeException("Failed to execute SPARQL query", e);
        }
        
        return results;
    }
    
    /**
     * Get all triples related to a subject
     */
    public List<Map<String, String>> getRelatedTriples(String subject) {
        String query = String.format(
            "PREFIX agi: <%s> " +
            "SELECT ?predicate ?object " +
            "WHERE { " +
            "  agi:%s ?predicate ?object . " +
            "}",
            namespace, subject
        );
        
        return querySparql(query);
    }
    
    /**
     * Perform inference and get inferred triples
     */
    public List<Map<String, String>> getInferredTriples() {
        List<Map<String, String>> inferred = new ArrayList<>();
        
        try {
            StmtIterator iter = infModel.listStatements();
            
            while (iter.hasNext()) {
                Statement stmt = iter.nextStatement();
                
                // Check if this is an inferred statement
                if (!model.contains(stmt)) {
                    Map<String, String> triple = new HashMap<>();
                    triple.put("subject", stmt.getSubject().toString());
                    triple.put("predicate", stmt.getPredicate().toString());
                    triple.put("object", stmt.getObject().toString());
                    inferred.add(triple);
                }
            }
            
            logger.debug("Found {} inferred triples", inferred.size());
        } catch (Exception e) {
            logger.error("Error getting inferred triples", e);
        }
        
        return inferred;
    }
    
    /**
     * Get statistics about the knowledge graph
     */
    public Map<String, Long> getStatistics() {
        Map<String, Long> stats = new HashMap<>();
        
        stats.put("total_triples", model.size());
        stats.put("inferred_triples", infModel.size() - model.size());
        
        // Count unique subjects
        long uniqueSubjects = model.listSubjects().toList().size();
        stats.put("unique_subjects", uniqueSubjects);
        
        // Count unique predicates
        long uniquePredicates = model.listStatements().toList().stream()
            .map(Statement::getPredicate)
            .distinct()
            .count();
        stats.put("unique_predicates", uniquePredicates);
        
        logger.debug("Knowledge graph statistics: {}", stats);
        return stats;
    }
    
    /**
     * Clear all data from the knowledge graph
     */
    public void clear() {
        model.removeAll();
        infModel = ModelFactory.createInfModel(reasoner, model);
        logger.info("Knowledge graph cleared");
    }
    
    /**
     * Export knowledge graph as RDF/XML
     */
    public String exportAsRdfXml() {
        java.io.StringWriter writer = new java.io.StringWriter();
        model.write(writer, "RDF/XML");
        return writer.toString();
    }
}
