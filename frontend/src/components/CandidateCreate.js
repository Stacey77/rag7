import React, { useState } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  Modal,
  Alert,
  CircularProgress,
} from "@mui/material";
import api from "../api";

const modalStyle = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: 560,
  bgcolor: "background.paper",
  boxShadow: 24,
  p: 3,
};

export default function CandidateCreate({ open, onClose, onCreated }) {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [appliedRole, setAppliedRole] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const resetForm = () => {
    setFullName("");
    setEmail("");
    setAppliedRole("");
    setResumeFile(null);
    setError(null);
  };

  const handleFileChange = (e) => {
    setResumeFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!fullName || !email) {
      setError("Full name and email are required.");
      return;
    }

    const fd = new FormData();
    fd.append("full_name", fullName);
    fd.append("email", email);
    if (appliedRole) fd.append("applied_role", appliedRole);
    if (resumeFile) fd.append("resume", resumeFile);

    setSubmitting(true);
    try {
      const resp = await api.post("candidates/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      const created = resp.data;
      resetForm();
      if (onCreated) onCreated(created);
    } catch (err) {
      console.error("Candidate create error:", err);
      const detail =
        err?.response?.data?.detail ||
        err?.response?.data ||
        "Failed to create candidate.";
      if (typeof detail === "object") {
        const msgs = Object.entries(detail)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
          .join(" — ");
        setError(msgs || JSON.stringify(detail));
      } else {
        setError(detail);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal open={!!open} onClose={onClose}>
      <Box component="form" onSubmit={handleSubmit} sx={modalStyle}>
        <Typography variant="h6" gutterBottom>
          New Candidate
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <TextField
          label="Full name"
          fullWidth
          required
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          sx={{ mb: 2 }}
        />
        <TextField
          label="Email"
          fullWidth
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          sx={{ mb: 2 }}
        />
        <TextField
          label="Applied role"
          fullWidth
          value={appliedRole}
          onChange={(e) => setAppliedRole(e.target.value)}
          sx={{ mb: 2 }}
        />

        <Box sx={{ mb: 2 }}>
          <input id="candidate-resume" type="file" accept=".pdf,.txt,.doc,.docx" onChange={handleFileChange} />
        </Box>

        <Box display="flex" justifyContent="flex-end" gap={2}>
          <Button onClick={onClose} disabled={submitting}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={submitting}>{submitting ? <CircularProgress size={20} /> : "Create"}</Button>
        </Box>
      </Box>
    </Modal>
  );
}
