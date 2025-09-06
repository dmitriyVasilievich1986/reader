import { useState, useEffect } from "react";
import { NavLink } from "react-router";

import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import { RisonClass, call } from "../../support/caller";
import { AvailableMenus, MenuType } from "./types";
import { Breadcrumbs } from "./Breadcrumbs";

const HOME: MenuType = { label: AvailableMenus.Home, url: "/" };

export function Navbar() {
  const [menu, setMenu] = useState<MenuType[]>([]);

  useEffect(() => {
    call<MenuType[]>({
      method: "get",
      url: "/api/v1/menu/",
      onSucces: (result) => {
        setMenu(result.filter((m) => m.label in AvailableMenus));
      },
    });
  }, []);

  const getRison = (label: string) => {
    if (label === HOME.label) return "";
    return new RisonClass({ order_column: "name" }).call();
  };

  return (
    <>
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#15616d",
          color: "#ffecd1",
        }}
        height={100}
      >
        <Grid
          container
          spacing={4}
          columns={2}
          direction="row"
          wrap="nowrap"
          rowSpacing={4}
          width="100%"
          maxWidth={600}
        >
          <Grid
            size={4}
            justifyContent="center"
            container
            sx={{ cursor: "pointer" }}
          >
            <NavLink className="navlink" to={HOME.url}>
              {HOME.label}
            </NavLink>
          </Grid>
          {menu.map((item) => (
            <Grid
              key={item.label}
              size={4}
              justifyContent="center"
              container
              sx={{ cursor: "pointer" }}
            >
              <NavLink
                className="navlink"
                to={`${item.url}${getRison(item.label)}`}
              >
                {item.label}
              </NavLink>
            </Grid>
          ))}
        </Grid>
      </Box>
      <Breadcrumbs />
    </>
  );
}
