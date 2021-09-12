# ducky-demo
This project demonstrates the use of Hak5's USB rubber ducky to steal credentials and crack weak (keyboard pattern) passwords.

### This demo explains 2 concepts

1. USB Rubber Ducky - Any USB device claiming to be a Keyboard Human Interface Device (HID) will be automatically detected and accepted by most modern operating systems. Whether it is a Windows, Mac, Linux, or Android device the Keyboard is King. By taking advantage of this inherent trust, the USB Rubber Ducky can bypass traditional countermeasures with scripted keystrokes at speeds beyond 1000 words per minute. The USB Rubber Ducky can perform malicious activities to grant the attacker privileged access to target system. 

2. Password Cracking – Cracking a short password (8 characters or less) is trivial with modern computers. Password policies tend to enforce password length and complexity requirements to ensure high password entropy. However, humans aren't good at memorizing random symbols and characters, so they resort to patterns that will satisfy the password complexity requirements while still being memorable (https://ieeexplore.ieee.org/document/5375544). Keyboard patterns significantly reduce the problem space, making these types of passwords vulnerable to brute force attacks. The password cracking portion of this demo demonstrates this concept.

**NOTE:** To reduce the runtime of the password cracker, the following restrictions are assumed:
- Passwords use md5 hashing algo
- Passwords are exactly 12 characters
- Password pattern contains 3 sets of 4 contiguous keys or 4 sets of 3 contiguous keys

## Installation of Password Cracking Website
The password cracking website can be a standalone demo of password cracking. It can also be sent password hashes (i.e. by a USB rubber ducky payload) from another computer.

Commands here were tested on Ubuntu 16, but should work on any debian based distro like Kali.

### 1. Get dependencies
```
sudo apt dist-upgrade
sudo apt update
sudo apt install python-setuptools python-dev
sudo apt install build-essential
sudo apt install python-pip
sudo pip install Flask
sudo apt install ocl-icd-libopencl1
sudo apt install opencl-headers
sudo apt install clinfo
sudo apt install ocl-icd-opencl-dev
sudo apt install git
sudo apt install curl
```

### 2. Get OpenCL Working (Optional?)
NOTE: This section is highly dependent on what hardware your computer has. This method worked for our computers.
Hashcat will need OpenCL devices and headers to work properly. Unfortunately, Intel doesn’t support Ubuntu 16, so we need to do a bit of a workaround. First, go to https://software.intel.com/en-us/articles/opencl-drivers and download OpenCL Runtime 16.1.1 for Intel Core and Xeon Processors for Ubuntu (64-bit).
We will assume that downloaded .tgz file is in the user’s Downloads directory, though it doesn’t really matter.
Install a tool that will turn .rpm files to .deb:
```
sudo apt install –y rpm alien libnuma1
```

Go to the Downloads folder and unzip the OpenCL tar file:
```
cd ~/Downloads
tar –xvf opencl_runtime_16.1.1_x64_ubuntu_6.4.0.25.tgz
cd opencl_runtime_16.1.1_x64_ubuntu_6.4.0.25/rpm
```

Change .rpm files to .deb:
```
fakeroot alien -–to-deb opencl-1.2-base-6.4.0.25-1.x86_64.rpm
fakeroot alien –-to-deb opencl-1.2-intel-cpu-6.4.0.25-1.x86_64.rpm
```

Install .deb packages:
```
sudo dpkg –i opencl-1.2-base_6.4.0.25-2_amd64.deb
sudo dpkg –i opencl-1.2-intel-cpu_6.4.0.25-2_amd64.deb
sudo touch /etc/ld.so.conf.d/intelOpenCL.conf
```

Open the file
```
sudo vim /etc/ld.so.conf.d/intelOpenCL.conf
```
and add the line
	`/opt/intel/opencl-1.2-6.4.0.25/lib64/clinfo`

Create a vendor and link files:
```
sudo mkdir –p /etc/OpenCL/vendors
sudo ln /opt/intel/opencl-1.2-6.4.0.25/etc/intel64.icd /etc/OpenCL/vendors/intel64.icd
sudo ldconfig
```

To test if this work, run `clinfo` and check the output, it should list OpenCL devices.

### 3. Getting Hashcat and the pyHashcat Interface
To set up pyHashcat, clone the git repository. The key here is that we actually build Hashcat inside the pyHashcat directory.
```
git clone https://github.com/Rich5/pyHashcat.git
cd pyHashcat/pyhashcat/
git clone https://github.com/hashcat/hashcat.git
cd hashcat/
git submodule init
git submodule update
sudo make install_library
sudo make
sudo make install
cd ..
python setup.py build_ext –R /usr/local/lib
sudo python setup.py install
```

To test if everything is working, run python `test.py` in the pyhashcat directory. Hashcat should run and crack a single hash.
Setting up the Website

### 4. Getting wordlist

Download the wordlist from https://drive.google.com/drive/folders/1J6NDuljCyVdk5iFEwjPNzp7EfsSwsg3G?usp=sharing

By default, our wordlist “princeCombo.txt” should be under ~/Documents/wordlist/. This wordlist contains about 693 million length 12 parallel-4 and parallel-3 passwords.

### 5. Start the web server
```
python PasswordCracking.py
```
Then open a web browser and connect to 127.0.0.1:5000 to access the site.

### 6. To do a fresh demo
```
rm demo_password_table.db
sudo python PasswordCracking.py
```
