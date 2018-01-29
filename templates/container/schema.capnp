@0x8a720f7e23b49550;


struct Schema {
    node @0 :Text; # pointer to the parent service
    hostname @1 :Text;
    flist @2 :Text; # Url to the root filesystem flist
    initProcesses @3 :List(Process);
    nics @4 :List(Nic); # Configuration of the attached nics to the container
    hostNetworking @5 :Bool;
    # Make host networking available to the guest.
    # If true means that the container will be able participate in the networks available in the host operating system.
    ports @6:List(Text); # List of node to container post mappings. e.g: 8080:80
    storage @7 :Text;
    mounts @8: List(Mount); # List mount points mapping to the container
    bridges @9 :List(Text); # comsumed bridges, automaticly filled don't pass in blueprint
    zerotiernodeid @10:Text;
    privileged @11 :Bool;
    identity @12 :Text;

    struct Mount {
        filesystem @0 :Text; # Instance name of a filesystem service
        target @1 :Text; # where to mount this filesystem in the container
    }

    struct Process {
        name @0 :Text; # Name of the executable that needs to be run
        pwd @1 :Text; # Directory in which the process needs to be started
        args @2 :List(Text); #  List of commandline arguments
        environment @3 :List(Text);
        # Environment variables for the process.
        # e.g:  'PATH=/usr/bin/local'
        stdin @4 :Text; # Data that needs to be passed into the stdin of the started process
        id @5: Text;
    }

    struct Nic {
        type @0: NicType;
        id @1: Text;
        config @2: NicConfig;
        name @3: Text;
        token @4: Text;
        hwaddr @5: Text;
    }

    struct NicConfig {
        dhcp @0: Bool;
        cidr @1: Text;
        gateway @2: Text;
        dns @3: List(Text);
    }

    enum NicType {
        default @0;
        zerotier @1;
        vlan @2;
        vxlan @3;
        bridge @4;
    }
}
