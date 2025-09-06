import { useSearchParams } from "react-router";
import { useState, useEffect } from "react";
import rison from "rison";

import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";

import { RisonFilterClass, RisonClass, call } from "../../support/caller";
import { AuthorType, BookType } from "../../types";
import { BookCard } from "../../components";

export function BooksPage() {
  const [authors, setAuthors] = useState<AuthorType[]>([]);
  const [books, setBooks] = useState<BookType[]>([]);

  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    let q = searchParams.get("q");
    if (!q) {
      q = rison.encode(new RisonClass({ order_column: "name" }));
      setSearchParams({ q });
    }
    const r = new RisonClass(rison.decode(q));
    call<BookType[]>({
      method: "get",
      url: `/api/v1/book/${r.call()}`,
      onSucces: setBooks,
    });
  }, [searchParams]);

  const getAuthors = () => {
    call<AuthorType[]>({
      method: "get",
      url: "/api/v1/author",
      onSucces: setAuthors,
    });
  };

  const onChangeHandler = (author: AuthorType | null) => {
    const r = new RisonClass(rison.decode(searchParams.get("q")));
    r.filters =
      author === null
        ? []
        : [
            new RisonFilterClass({
              col: "author",
              opr: "rel_o_m",
              value: author.id,
            }),
          ];
    setSearchParams({ q: rison.encode(r) });
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 2 }} sx={{ p: 1 }}>
          <Box sx={{ display: "flex", justifyContent: "center" }}>
            <Autocomplete
              onChange={(_, v) => onChangeHandler(v)}
              getOptionLabel={(option) => option.name}
              getOptionKey={(option) => option.id}
              disablePortal
              onOpen={getAuthors}
              options={authors}
              sx={{ width: "90%", maxWidth: "300px" }}
              renderInput={(params) => (
                <TextField {...params} label="Authors" />
              )}
            />
          </Box>
        </Grid>
        <Grid size={{ xs: 12, sm: 12, md: 9 }}>
          <Grid container spacing={2} sx={{ p: 1 }} justifyContent="center">
            {books.map((book) => (
              <BookCard book={book} key={book.id} />
            ))}
          </Grid>
        </Grid>
        <Grid
          size={{ xs: 12, md: 1 }}
          sx={{ display: { xs: "none", md: "block" } }}
        ></Grid>
      </Grid>
    </Box>
  );
}
