import { useSearchParams } from "react-router";
import { useState, useEffect } from "react";
import { BookType } from "../../types";

import Divider from "@mui/material/Divider";
import Chip from "@mui/material/Chip";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";

import { RisonClass, call } from "../../support/caller";
import { BookCard } from "../../components";

export function HomePage() {
  const [mostViewedBooks, setMostViewedBooks] = useState<BookType[]>([]);
  const [newestBooks, setNewestBooks] = useState<BookType[]>([]);

  const [searchParams] = useSearchParams();

  useEffect(() => {
    const mostViewdRison = new RisonClass({
      page_size: 4,
      order_column: "views",
      order_direction: "desc",
    });
    const newestRison = new RisonClass({
      page_size: 4,
      order_column: "created_at",
      order_direction: "desc",
    });

    call<BookType[]>({
      method: "get",
      url: `/api/v1/book/${mostViewdRison.call()}`,
      onSuccess: setMostViewedBooks,
    });

    call<BookType[]>({
      method: "get",
      url: `/api/v1/book/${newestRison.call()}`,
      onSuccess: setNewestBooks,
    });
  }, [searchParams]);

  return (
    <Box>
      <Divider sx={{ margin: "1rem 0" }} variant="middle">
        <Chip label="Popular" size="small" />
      </Divider>
      <Grid container spacing={2} sx={{ p: 1 }} justifyContent="center">
        {mostViewedBooks.map((book) => (
          <BookCard book={book} key={book.id} />
        ))}
      </Grid>
      <Divider sx={{ margin: "1rem 0" }} variant="middle">
        <Chip label="New" size="small" />
      </Divider>
      <Grid container spacing={2} sx={{ p: 1 }} justifyContent="center">
        {newestBooks.map((book) => (
          <BookCard book={book} key={book.id} />
        ))}
      </Grid>
      <Box sx={{ height: "5rem" }} />
    </Box>
  );
}
