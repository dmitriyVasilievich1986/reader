import { useSearchParams } from "react-router";
import { useState, useEffect } from "react";
import rison from "rison";

import ListItem from "@mui/material/ListItem";
import Grid from "@mui/material/Grid2";
import List from "@mui/material/List";

import { RisonClass, call } from "../../support/caller";
import { PageType } from "./types";

export function BookPage() {
  const [pages, setPages] = useState<PageType[]>([]);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const r = new RisonClass(rison.decode(searchParams.get("q")));
    call<PageType[]>({
      method: "get",
      url: `/api/v1/page/${r.call()}`,
      onSucces: setPages,
    });
  }, [searchParams]);

  return (
    <List>
      {pages.map((page) => (
        <ListItem disablePadding key={page.position}>
          <Grid justifyContent="center" container width="100vw">
            <img
              style={{ width: "90vw", maxWidth: "900px" }}
              src={page.cover}
            />
          </Grid>
        </ListItem>
      ))}
    </List>
  );
}
