import React, { useEffect, useState } from "react";
import "./PeopleTable.css";
import { Table, Tag } from "antd";
import Filters from "../Filters/Filters";

const PeopleTable = () => {
  const [state, setState] = useState({
    data: [],
    pagination: {
      current: 1,
      pageSize: 10,
    },
    loading: false,
  });

  const { data, pagination, loading } = state;

  const [filter, setFilter] = useState({ gender: "", knownfor: "" });
  const [pgn, setPgn] = useState({ page: 1, limit: 10 });

  const getData = (params = {}) => {
    setState({ loading: true });
    let searchParams = { ...filter, ...pgn };
    fetch(
      `http://127.0.0.1:5000/getpeople?` + new URLSearchParams(searchParams)
    )
      .then((res) => res.json())
      .then((res) => {
        setState({
          loading: false,
          data: res.data,
          pagination: {
            ...params.pagination,
            total: res.total,
          },
        });
      });
  };

  useEffect(() => {
    getData();
  }, [pgn, filter]);

  const getFilter = (flt) => {
    let newFilter = filter;
    let key = Object.keys(flt)[0];
    newFilter[key] = flt[key];
    setFilter(newFilter);
    console.log(filter);
    let newPagination = pagination;
    pagination.current = 1;
    setState({pagination: newPagination})
    getData();
  };

  const columns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "Gender",
      dataIndex: "gender",
      key: "gender",
    },
    {
      title: "Known For",
      dataIndex: "known_for_department",
      key: "known_for_department",
    },
    {
      title: "Popularity",
      key: "popularity",
      dataIndex: "popularity",
      render: (pop) => {
        let color = "";
        if (pop < 5) color = "red";
        if (pop >= 5 && pop < 10) color = "volcano";
        if (pop >= 10 && pop < 15) color = "lime";
        if (pop >= 15 && pop < 20) color = "green";
        if (pop >= 20) color = "geekblue";

        return (
          <span>
            <Tag color={color} key={pop}>
              {pop}
            </Tag>
          </span>
        );
      },
    },
  ];

  const handleTableChange = (pagination) => {
    setPgn({ page: pagination.current, limit: pagination.pageSize });
  };

  return (
    <div className="PeopleTable">
      <Filters filterChanged={getFilter}></Filters>
      <Table
        columns={columns}
        dataSource={data}
        pagination={pagination}
        loading={loading}
        onChange={handleTableChange}
      />
    </div>
  );
};

PeopleTable.propTypes = {};

PeopleTable.defaultProps = {};

export default PeopleTable;
