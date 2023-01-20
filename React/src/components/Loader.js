import React from "react";
import CircularProgress from "@mui/material/CircularProgress";
import Box from "@mui/material/Box";
import { Container } from "@mui/material";

export default function Loader() {
  return (
    <Container
      maxWidth="sm"
      fixed
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "80vh",
      }}
    >
      <Box>
        <CircularProgress />
      </Box>
    </Container>
  );
}
