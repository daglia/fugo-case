import React, { useState, useEffect } from "react";
import "./Filters.css";
import { Select, Form, Row, Col } from "antd";
import PropTypes from "prop-types";

const { Option } = Select;

const layout = {
  labelCol: { span: 8 },
  wrapperCol: { span: 16 },
};

const Filters = ({ filterChanged }) => {
  const [data, setData] = useState({ genders: [], knownfors: [] });

  useEffect(() => {
    fetch("http://127.0.0.1:5000/getfilterdata")
      .then((response) => response.json())
      .then((data) => {
        setData({ genders: data.genders, knownfors: data.knownfors });
      });
  }, []);

  const handleGenderChange = (val) => {
    filterChanged({ gender: val });
  };

  const handleKnownForChange = (val) => {
    filterChanged({ knownfor: val });
  };

  return (
    <div>
      <Form {...layout}>
        <Row>
          <Col span={8}>
            <Form.Item name="gender" label="Gender">
              <Select defaultValue="" onChange={handleGenderChange}>
                <Option value="">All</Option>
                {data.genders.map((g) => (
                  <Option value={g}>{g}</Option>
                ))}
                ;
              </Select>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item name="knownfor" label="Known For">
              <Select defaultValue="" onChange={handleKnownForChange}>
                <Option value="">All</Option>
                {data.knownfors.map((k) => (
                  <Option value={k}>{k}</Option>
                ))}
                ;
              </Select>
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </div>
  );
};

Filters.propTypes = {
  gender: PropTypes.string,
  knownfor: PropTypes.string,
};

Filters.defaultProps = { gender: "", knownfor: "" };

export default Filters;
