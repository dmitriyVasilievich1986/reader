import { useSearchParams, Link } from "react-router";
import { BookType } from "../../types";

import Card from "@mui/material/Card";
import CardHeader from "@mui/material/CardHeader";
import CardMedia from "@mui/material/CardMedia";
import CardActions from "@mui/material/CardActions";
import VisibilityIcon from "@mui/icons-material/Visibility";

import classnames from "classnames/bind";
import * as style from "./style.scss";

const cx = classnames.bind(style);

export function BookCard(props: { book: BookType }) {
  const [searchParams] = useSearchParams();

  return (
    <Card variant="outlined" className={cx("book-card")}>
      <CardMedia component="img" height="300" image={props.book.cover} />
      <CardHeader
        title={
          <Link to={`/book/${props.book.id}?${searchParams.toString()}`}>
            {props.book.name}
          </Link>
        }
        subheader={`@${props.book.author_name}`}
      />
      <CardActions disableSpacing>
        <VisibilityIcon />
        {props.book.views}
      </CardActions>
    </Card>
  );
}
