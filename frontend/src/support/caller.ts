import axios from "axios";
import rison from "rison";

type ResponseType<R> = {
  data: {
    ids: number[];
    result: R;
  };
};

export function call<R>(props: {
  method: "get" | "post" | "put";
  url: string;
  data?: any;
  onSucces?: (response: R) => void;
  onFail?: () => void;
}) {
  axios(props)
    .then((response: ResponseType<R>) => {
      props?.onSucces && props.onSucces(response.data.result);
    })
    .catch((error) => {
      console.log(error);
      props?.onFail && props.onFail();
    });
}

export class RisonFilterClass {
  col: string;
  opr: "rel_o_m";
  value: number | string;

  constructor(props: { col: string; opr: "rel_o_m"; value: number | string }) {
    this.col = props.col;
    this.opr = props.opr;
    this.value = props.value;
  }
}

export class RisonClass {
  filters?: RisonFilterClass[];
  order_column?: string;
  order_direction: "desc" | "asc" = "asc";
  page: number = 0;
  page_size: number = 50;

  constructor(props?: {
    filters?: RisonFilterClass[];
    order_column?: string;
    order_direction?: "desc" | "asc";
    page_size?: number;
    page?: number;
  }) {
    this.order_column = props.order_column;
    this.filters = props?.filters?.map((f) => new RisonFilterClass(f)) ?? [];

    this.order_direction = props?.order_direction || this.order_direction;
    this.page_size = props?.page_size || this.page_size;
    this.page = props?.page || this.page;
  }

  call() {
    const p = rison.encode(this);
    return `?q=${p}`;
  }
}
