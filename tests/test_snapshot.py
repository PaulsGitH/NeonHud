import json

from neonhud.models import snapshot


def test_snapshot_shape_and_types():
    snap = snapshot.build()
    # Top-level keys
    for k in ("schema", "timestamp", "host", "cpu", "memory", "disk_io", "net_io"):
        assert k in snap

    assert snap["schema"] == "neonhud.report.v1"
    assert isinstance(snap["timestamp"], str)

    host = snap["host"]
    assert isinstance(host, dict)
    for k in ("hostname", "os", "kernel"):
        assert k in host
        assert isinstance(host[k], str)

    cpu = snap["cpu"]
    assert isinstance(cpu, dict)
    assert "percent_total" in cpu and "per_cpu" in cpu
    assert isinstance(cpu["percent_total"], float)
    assert isinstance(cpu["per_cpu"], list)
    assert len(cpu["per_cpu"]) >= 1

    mem = snap["memory"]
    assert isinstance(mem, dict)
    for k in ("total", "used", "available", "percent"):
        assert k in mem
    assert isinstance(mem["total"], int)
    assert isinstance(mem["used"], int)
    assert isinstance(mem["available"], int)
    assert isinstance(mem["percent"], float)

    disk_io = snap["disk_io"]
    assert isinstance(disk_io, dict)
    assert "read_bytes" in disk_io and "write_bytes" in disk_io
    assert isinstance(disk_io["read_bytes"], int)
    assert isinstance(disk_io["write_bytes"], int)

    net_io = snap["net_io"]
    assert isinstance(net_io, dict)
    assert "bytes_sent" in net_io and "bytes_recv" in net_io
    assert isinstance(net_io["bytes_sent"], int)
    assert isinstance(net_io["bytes_recv"], int)

    # Ensure JSON-serializable
    json.dumps(snap)
