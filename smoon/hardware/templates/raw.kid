<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Raw Dump</title>
</head>
<body>
    <div py:for='host in Hosts'><table>
        <tr><td>UUID</td><td>${host.UUID}</td></tr>
        <tr><td>OS</td><td>${host.OS}</td></tr>
        <tr><td>platform</td><td>${host.platform}</td></tr>
        <tr><td>bogomips</td><td>${host.bogomips}</td></tr>
        <tr><td>systemMemory</td><td>${host.systemMemory}</td></tr>
        <tr><td>systemSwap</td><td>${host.systemSwap}</td></tr>
        <tr><td>CPUVendor</td><td>${host.CPUVendor}</td></tr>
        <tr><td>numCPUs</td><td>${host.numCPUs}</td></tr>
        <tr><td>CPUSpeed</td><td>${host.CPUSpeed}</td></tr>
        <tr><td>language</td><td>${host.language}</td></tr>
        <tr><td>defaultRunlevel</td><td>${host.defaultRunlevel}</td></tr>
        <tr><td>vendor</td><td>${host.vendor}</td></tr>
        <tr><td>system</td><td>${host.system}</td></tr>
        <tr><td>selinux_enabled</td><td>${host.selinux_enabled}</td></tr>
        <tr><td>selinux_enforce</td><td>${host.selinux_enforce}</td></tr>
        </table>
            <table>
                <tr><th>Bus</th><th>Class</th><th>Driver</th><th>Description</th></tr>
            <div py:for='link in HostLinks.select("host_u_u_id=\"%s\"" % host.UUID)'>
                <tr>
                    <td>${Device.select('id=%s' % link.deviceID)[0].Bus}</td>
                    <td>${Device.select('id=%s' % link.deviceID)[0].Class}</td>
                    <td>${Device.select('id=%s' % link.deviceID)[0].Driver}</td>
                    <td>${Device.select('id=%s' % link.deviceID)[0].Description}</td>
                </tr>
            </div>
            </table>
        <br/>
    </div>
</body>
</html>
