import { useLocation, useSearchParams } from "react-router";
import React from "react";

import { default as MUIBreadcrumbs } from "@mui/material/Breadcrumbs";
import Link from "@mui/material/Link";

import { PathNameType } from "./types";

export function Breadcrumbs() {
  const location = useLocation();
  const [searchParams] = useSearchParams();

  const [pathNames, setPathNames] = React.useState<PathNameType[]>([]);

  React.useEffect(() => {
    const pathnames = location.pathname.split("/").filter((x) => x);
    const newPathNames = pathnames.map((value, index) => {
      const q = searchParams.get("q");
      const to = `/${pathnames.slice(0, index + 1).join("/")}${
        q ? `?q=${q}` : ""
      }`;
      return { label: value, to };
    });
    setPathNames(newPathNames);
  }, [location, searchParams]);

  return (
    <div
      style={{
        position: "sticky",
        top: 0,
        backgroundColor: "#fff",
        zIndex: 10,
        padding: "0.5rem 2rem",
      }}
    >
      <MUIBreadcrumbs aria-label="breadcrumb">
        <Link underline="hover" color="inherit" href="/">
          Home
        </Link>
        {pathNames.map((segment) => (
          <Link href={segment.to} key={segment.to}>
            {segment.label}
          </Link>
        ))}
      </MUIBreadcrumbs>
    </div>
  );
}
