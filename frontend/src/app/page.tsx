"use client";

import { Container, Grid, Typography } from "@mui/material";
import UploadCard from "@/components/UploadCard";
import ChatCard from "@/components/ChatCard";
import { useEffect } from "react";
import { getSessionId, resetSessionId } from "@/lib/session";
import { Button, Box } from "@mui/material";

export default function HomePage() {
  // ensure session exists on first load
  useEffect(() => {
    getSessionId();
  }, []);

  const handleResetSession = () => {
    resetSessionId();
    window.location.reload();
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        AI Resume Analyzer
      </Typography>
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 5 }}>
          <UploadCard />
          <Box sx={{ mt: 2 }}>
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleResetSession}
            >
              Reset Session
            </Button>
          </Box>
        </Grid>
        <Grid
          size={{ xs: 12, md: 7 }}
          sx={{ minHeight: 480, maxHeight: "80vh" }}
        >
          <ChatCard />
        </Grid>
      </Grid>
    </Container>
  );
}
