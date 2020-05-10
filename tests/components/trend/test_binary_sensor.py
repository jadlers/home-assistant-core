"""The test for the Trend sensor platform."""
from datetime import timedelta

from homeassistant import setup
import homeassistant.util.dt as dt_util

from tests.async_mock import patch
from tests.common import assert_setup_component, get_test_home_assistant


class TestTrendBinarySensor:
    """Test the Trend sensor."""

    hass = None

    def setup_method(self, method):
        """Set up things to be run when tests are started."""
        self.hass = get_test_home_assistant()

    def teardown_method(self, method):
        """Stop everything that was started."""
        self.hass.stop()

    def test_up(self):
        """Test up trend."""
        assert setup.setup_component(
            self.hass,
            "binary_sensor",
            {
                "binary_sensor": {
                    "platform": "trend",
                    "sensors": {
                        "test_trend_sensor": {"entity_id": "sensor.test_state"}
                    },
                }
            },
        )

        self.hass.states.set("sensor.test_state", "1")
        self.hass.block_till_done()
        self.hass.states.set("sensor.test_state", "2")
        self.hass.block_till_done()
        state = self.hass.states.get("binary_sensor.test_trend_sensor")
        assert state.state == "on"

    def test_up_using_trendline(self):
        """Test up trend using multiple samples and trendline calculation."""
        assert setup.setup_component(
            self.hass,
            "binary_sensor",
            {
                "binary_sensor": {
                    "platform": "trend",
                    "sensors": {
                        "test_trend_sensor": {
                            "entity_id": "sensor.test_state",
                            "sample_duration": 10000,
                            "min_gradient": 1,
                            "max_samples": 25,
                        }
                    },
                }
            },
        )

        now = dt_util.utcnow()
        for val in [10, 0, 20, 30]:
            with patch("homeassistant.util.dt.utcnow", return_value=now):
                self.hass.states.set("sensor.test_state", val)
            self.hass.block_till_done()
            now += timedelta(seconds=2)

        state = self.hass.states.get("binary_sensor.test_trend_sensor")
        assert state.state == "on"

        # have to change state value, otherwise sample will lost
        for val in [0, 30, 1, 0]:
            with patch("homeassistant.util.dt.utcnow", return_value=now):
                self.hass.states.set("sensor.test_state", val)
            self.hass.block_till_done()
            now += timedelta(seconds=2)

        state = self.hass.states.get("binary_sensor.test_trend_sensor")
        assert state.state == "off"

    def test_down_using_trendline(self):
        """Test down trend using multiple samples and trendline calculation."""
        assert setup.setup_component(
            self.hass,
            "binary_sensor",
            {
                "binary_sensor": {
                    "platform": "trend",
                    "sensors": {
                        "test_trend_sensor": {
                            "entity_id": "sensor.test_state",
                            "sample_duration": 10000,
                            "min_gradient": 1,
                            "max_samples": 25,
                            "invert": "Yes",
                        }
                    },
                }
            },
        )

        now = dt_util.utcnow()
        for val in [30, 20, 30, 10]:
            with patch("homeassistant.util.dt.utcnow", return_value=now):
                self.hass.states.set("sensor.test_state", val)
            self.hass.block_till_done()
            now += timedelta(seconds=2)

        state = self.hass.states.get("binary_sensor.test_trend_sensor")
        assert state.state == "on"

        for val in [30, 0, 45, 50]:
            with patch("homeassistant.util.dt.utcnow", return_value=now):
                self.hass.states.set("sensor.test_state", val)
            self.hass.block_till_done()
            now += timedelta(seconds=2)

        state = self.hass.states.get("binary_sensor.test_trend_sensor")
        assert state.state == "off"

    def test_down(self):
        """Test down trend."""
        assert setup.setup_component(
            self.hass,
            "binary_sensor",
            {
                "binary_sensor": {
                    "platform": "trend",
                    "sensors": {
                        "test_trend_sensor": {"entity_id": "sensor.test_state"}
                    },
                }
            },
        )

        self.hass.states.set("sensor.test_state", "2")
        self.hass.block_till_done()
        self.hass.states.set("sensor.test_state", "1")
        self.hass.block_till_done()
        state = self.hass.states.get("binary_sensor.test_trend_sensor")
        assert state.state == "off"

    def test_invert_up(self):
        """Test up trend with custom message."""
        assert setup.setup_component(
            self.hass,
            "binary_sensor",
            {
                "binary_sensor": {
                    "platform": "trend",
                    "sensors": {
                        "test_trend_sensor": {
                            "entity_id": "sensor.test_state",
                            "invert": "Yes",
                        }
                    },
                }
            },
        )

        self.hass.states.set("sensor.test_state", "1")
        self.hass.block_till_done()
        self.hass.states.set("sensor.test_state", "2")
        self.hass.block_till_done()
        state = self.hass.states.get("binary_sensor.test_trend_sensor")
        assert state.state == "off"

    def test_invert_down(self):
        """Test down trend with custom message."""
        assert setup.setup_component(
            self.hass,
            "binary_sensor",
            {
                "binary_sensor": {
                    "platform": "trend",
                    "sensors": {
                        "test_trend_sensor": {
                            "entity_id": "sensor.test_state",
                            "invert": "Yes",
                        }
                    },
                }
            },
        )

        self.hass.states.set("sensor.test_state", "2")
        self.hass.block_till_done()
        self.hass.states.set("sensor.test_state", "1")
        self.hass.block_till_done()
        state = self.hass.states.get("binary_sensor.test_trend_sensor")
        assert state.state == "on"

    def test_attribute_up(self):
        """Test attribute up trend."""
        assert setup.setup_component(
            self.hass,
            "binary_sensor",
            {
                "binary_sensor": {
                    "platform": "trend",
                    "sensors": {
                        "test_trend_sensor": {
                            "entity_id": "sensor.test_state",
                            "attribute": "attr",
                        }
                    },
                }
            },
        )
        self.hass.states.set("sensor.test_state", "State", {"attr": "1"})
        self.hass.block_till_done()
        self.hass.states.set("sensor.test_state", "State", {"attr": "2"})
        self.hass.block_till_done()
        state = self.hass.states.get("binary_sensor.test_trend_sensor")
        assert state.state == "on"

    def test_attribute_down(self):
        """Test attribute down trend."""
        assert setup.setup_component(
            self.hass,
            "binary_sensor",
            {
                "binary_sensor": {
                    "platform": "trend",
                    "sensors": {
                        "test_trend_sensor": {
                            "entity_id": "sensor.test_state",
                            "attribute": "attr",
                        }
                    },
                }
            },
        )

        self.hass.states.set("sensor.test_state", "State", {"attr": "2"})
        self.hass.block_till_done()
        self.hass.states.set("sensor.test_state", "State", {"attr": "1"})
        self.hass.block_till_done()
        state = self.hass.states.get("binary_sensor.test_trend_sensor")
        assert state.state == "off"

    def test_max_samples(self):
        """Test that sample count is limited correctly."""
        assert setup.setup_component(
            self.hass,
            "binary_sensor",
            {
                "binary_sensor": {
                    "platform": "trend",
                    "sensors": {
                        "test_trend_sensor": {
                            "entity_id": "sensor.test_state",
                            "max_samples": 3,
                            "min_gradient": -1,
                        }
                    },
                }
            },
        )

        for val in [0, 1, 2, 3, 2, 1]:
            self.hass.states.set("sensor.test_state", val)
            self.hass.block_till_done()

        state = self.hass.states.get("binary_sensor.test_trend_sensor")
        assert state.state == "on"
        assert state.attributes["sample_count"] == 3

    def test_non_numeric(self):
        """Test up trend."""
        assert setup.setup_component(
            self.hass,
            "binary_sensor",
            {
                "binary_sensor": {
                    "platform": "trend",
                    "sensors": {
                        "test_trend_sensor": {"entity_id": "sensor.test_state"}
                    },
                }
            },
        )

        self.hass.states.set("sensor.test_state", "Non")
        self.hass.block_till_done()
        self.hass.states.set("sensor.test_state", "Numeric")
        self.hass.block_till_done()
        state = self.hass.states.get("binary_sensor.test_trend_sensor")
        assert state.state == "off"

    def test_missing_attribute(self):
        """Test attribute down trend."""
        assert setup.setup_component(
            self.hass,
            "binary_sensor",
            {
                "binary_sensor": {
                    "platform": "trend",
                    "sensors": {
                        "test_trend_sensor": {
                            "entity_id": "sensor.test_state",
                            "attribute": "missing",
                        }
                    },
                }
            },
        )

        self.hass.states.set("sensor.test_state", "State", {"attr": "2"})
        self.hass.block_till_done()
        self.hass.states.set("sensor.test_state", "State", {"attr": "1"})
        self.hass.block_till_done()
        state = self.hass.states.get("binary_sensor.test_trend_sensor")
        assert state.state == "off"

    def test_invalid_name_does_not_create(self):
        """Test invalid name."""
        with assert_setup_component(0):
            assert setup.setup_component(
                self.hass,
                "binary_sensor",
                {
                    "binary_sensor": {
                        "platform": "template",
                        "sensors": {
                            "test INVALID sensor": {"entity_id": "sensor.test_state"}
                        },
                    }
                },
            )
        assert self.hass.states.all() == []

    def test_invalid_sensor_does_not_create(self):
        """Test invalid sensor."""
        with assert_setup_component(0):
            assert setup.setup_component(
                self.hass,
                "binary_sensor",
                {
                    "binary_sensor": {
                        "platform": "template",
                        "sensors": {
                            "test_trend_sensor": {"not_entity_id": "sensor.test_state"}
                        },
                    }
                },
            )
        assert self.hass.states.all() == []

    def test_no_sensors_does_not_create(self):
        """Test no sensors."""
        with assert_setup_component(0):
            assert setup.setup_component(
                self.hass, "binary_sensor", {"binary_sensor": {"platform": "trend"}}
            )
        assert self.hass.states.all() == []
