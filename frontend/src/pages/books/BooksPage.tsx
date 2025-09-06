import { useSearchParams, Link } from "react-router";
import { useState, useEffect } from "react";
import rison from "rison";

import ImageListItem from "@mui/material/ImageListItem";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import ImageListItemBar from "@mui/material/ImageListItemBar";

import { RisonFilterClass, RisonClass, call } from "../../support/caller";
import { AuthorType, BookType } from "./types";

export function BooksPage() {
  const [authors, setAuthors] = useState<AuthorType[]>([]);
  const [books, setBooks] = useState<BookType[]>([]);

  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    const r = new RisonClass(rison.decode(searchParams.get("q")));
    call<BookType[]>({
      method: "get",
      url: `/api/v1/book/${r.call()}`,
      onSucces: setBooks,
    });
  }, [searchParams]);

  const getRison = (bookId: number) => {
    return new RisonClass({
      filters: [
        new RisonFilterClass({ col: "book", opr: "rel_o_m", value: bookId }),
      ],
      order_column: "position",
    }).call();
  };

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
              <ImageListItem key={book.id}>
                <Link to={`/book/${book.id}?${searchParams.toString()}`}>
                  <img
                    src={book.cover}
                    style={{ height: 300, width: 200 }}
                    loading="lazy"
                  />
                </Link>
                <ImageListItemBar
                  sx={{
                    maxWidth: "150px",
                    textOverflow: "clip",
                    overflowX: "hidden",
                  }}
                  subtitle={<span>by: @{book.author_name}</span>}
                  title={book.name}
                  position="below"
                />
              </ImageListItem>
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
