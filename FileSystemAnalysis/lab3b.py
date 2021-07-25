#!/usr/bin/python
# NAME: Khoa Quach, Joshua Futterman
# EMAIL: khoaquachschool@gmail.com, joshafuttcomp23@ucla.edu
# ID: 105123806,505347668

import sys
import csv

# Class Structures


class SUPERBLOCK:
    def __init__(self, file):
        self.blocks_count = int(file[1])
        self.inode_count = int(file[2])
        self.block_size = int(file[3])
        self.inode_size = int(file[4])
        self.blocks_per_group = int(file[5])
        self.inodes_per_group = int(file[6])
        self.first_inode = int(file[7])


class GROUP:
    def __init__(self, file):
        self.group_num = int(file[1])
        self.total_num_of_blocks = int(file[2])
        self.total_num_of_inodes = int(file[3])
        self.num_free_blocks = int(file[4])
        self.num_free_indoes = int(file[5])
        self.block_bitmap = int(file[6])
        self.inode_bitmap = int(file[7])
        self.first_block_of_inode = int(file[8])


class DIRENT:
    def __init__(self, file):
        self.parent_inode_number = int(file[1])
        self.logical_byte_offset = int(file[2])
        self.inode_reference = int(file[3])
        self.entry_length = int(file[4])
        self.name_lenth = int(file[5])
        self.name = file[6]


class INDIRECT:
    def __init__(self, file):
        self.inode_num = int(file[1])
        self.level_of_indirection = int(file[2])
        self.logical_byte_offset = int(file[3])
        self.block_of_indirect = int(file[4])
        self.block_of_reference = int(file[5])


class INODE:
    def __init__(self, file):
        self.inode_num = int(file[1])
        self.file_type = file[2]
        self.mode = int(file[3])
        self.owner = int(file[4])
        self.group = int(file[5])
        self.link_count = int(file[6])
        self.inode_change_time = file[7]
        self.mod_time = file[8]
        self.last_time_access = file[9]
        self.file_size = int(file[10])
        self.num_blocks = int(file[11])
        self.direct_pointer = [int(j) for j in file[12:24]]
        self.indirect_pointer = [int(j) for j in file[24:27]]


def Block_helper(block, offset, inode, level, output, blocktype):
    # Single indirect block
    if block < 0 or block > superblock.blocks_count:
        print("INVALID " + output + blocktype + "BLOCK " + str(block) + " IN INODE " +
              str(inode) + " AT OFFSET " + str(offset))
        inconsistencies = 1
    elif block > 0 and block < min_block:
        print("RESERVED " + output + blocktype + "BLOCK " + str(block) + " IN INODE " +
              str(inode) + " AT OFFSET " + str(offset))
        inconsistencies = 1
    # Check duplicates
    elif block != 0:
        # If duplicate print out
        if block in referencedList:
            dup_type = ""
            if referencedList[block][2] == 1:
                dup_type = "INDIRECT "
            elif referencedList[block][2] == 2:
                dup_type = "DOUBLE INDIRECT "
            elif referencedList[block][2] == 3:
                dup_type = "TRIPLE INDIRECT "

            print("DUPLICATE " + dup_type + "BLOCK " + str(block) + " IN INODE " +
                  str(referencedList[block][0]) + " AT OFFSET " +
                  str(referencedList[block][1]))

            print("DUPLICATE " + output + blocktype + "BLOCK " + str(block) + " IN INODE " +
                  str(inode) + " AT OFFSET " +
                  str(offset))
            inconsistencies = 1
        else:
            # First reference add to list
            referencedList[block] = [
                inode, offset, level]


def Block_consistency_audits():
    # referencedlist structure [inode number, offset, dup type]
    # Check for Block Consistency Audits
    offsetlist = [12, 268, 65804]
    outputlist = ["", "DOUBLE ", "TRIPLE "]
    for i in inode:
        # Inode not in directory
        if i.file_type == 's' and i.file_size <= superblock.blocks_count:
            continue

        offset = 0
        # direct blocks in indoe check
        for direct in i.direct_pointer:
            Block_helper(direct, offset, i.inode_num, "NONE", "", "")
            offset = offset + 1

        # indirect blocks in inode check
        for w in range(0, 3):
            Block_helper(
                i.indirect_pointer[w], offsetlist[w], i.inode_num, w+1, outputlist[w], "INDIRECT ")

    # Indirect block check
    for i in indirect:
        blocktype = "" if i.level_of_indirection < 0 else "INDIRECT "
        Block_helper(i.block_of_reference, i.logical_byte_offset, i.inode_num,
                     i.level_of_indirection, outputlist[i.level_of_indirection-1], blocktype)

    # Allocated blocks and unreferenced blocks
    for i in range(min_block, superblock.blocks_count):
        if i in Bfree and i in referencedList:
            print("ALLOCATED BLOCK " + str(i) + " ON FREELIST")
            inconsistencies = 1
        elif i not in Bfree and i not in referencedList:
            print("UNREFERENCED BLOCK " + str(i))
            inconsistencies = 1


def Inode_consistency_audits():
    # Inode consistency checks
    for inode in allocated_inodes:
        if inode in Ifree:
            print("ALLOCATED INODE " + str(inode) + " ON FREELIST")
            inconsistencies = 1

    for i in range(superblock.first_inode, superblock.inode_count):
        if i not in Ifree and i not in allocated_inodes:
            print("UNALLOCATED INODE " + str(i) + " NOT ON FREELIST")
            inconsistencies = 1


def directory_helper():
    # check invalid links counts
    for inodes in inode:
        counter = 0  # temporary counter
        for dir in dirent:
            if dir.inode_reference == inodes.inode_num:
                counter = counter + 1
        # if they don't match, print out error analysis
        if counter != inodes.link_count:
            print("INODE " + str(inodes.inode_num) + " HAS " + str(counter) +
                  " LINKS BUT LINKCOUNT IS " + str(inodes.link_count))
            inconsistencies = 1


def Directory_consistency_audits():
    directory_helper()
    parent = {2: 2}
    # check invalid unless than 1 or greater than inode counts) and unallocated inodes
    for dir in dirent:
        if dir.inode_reference < 1 or dir.inode_reference > superblock.inode_count:
            print("DIRECTORY INODE " + str(dir.parent_inode_number) + " NAME " +
                  dir.name + " INVALID INODE " + str(dir.inode_reference))
            inconsistencies = 1
        elif dir.inode_reference not in allocated_inodes:
            print("DIRECTORY INODE " + str(dir.parent_inode_number) + " NAME " +
                  dir.name + " UNALLOCATED INODE " + str(dir.inode_reference))
            inconsistencies = 1
        else:
            if dir.name != "'.'" and dir.name != "'..'":
                parent[dir.inode_reference] = dir.parent_inode_number
    # we have to check if they are respect to itself or parent
    for dir in dirent:
        if dir.name == "'.'":
            if dir.parent_inode_number != dir.inode_reference:
                print("DIRECTORY INODE " + str(dir.parent_inode_number) + " NAME " + dir.name +
                      " LINK TO INODE " + str(dir.inode_reference) + " SHOULD BE " + str(dir.parent_inode_number))
                inconsistencies = 1
        if dir.name == "'..'":
            if dir.parent_inode_number == 2:
                if dir.inode_reference != 2:  # root
                    print("DIRECTORY INODE " + str(dir.parent_inode_number) + " NAME " + dir.name +
                          " LINK TO INODE " + str(dir.inode_reference) + " SHOULD BE " + str(dir.parent_inode_number))
                    inconsistencies = 1
                elif dir.inode_reference != parent[dir.inode_reference]:
                    print("DIRECTORY INODE " + str(dir.parent_inode_number) + " NAME " + dir.name +
                          " LINK TO INODE " + str(dir.inode_reference) + " SHOULD BE " + parent[dir.inode_reference])
                    inconsistencies = 1


# Create globals
superblock = 0
group = 0
Ifree = []
Bfree = []
dirent = []
indirect = []
inode = []
min_block = 0
referencedList = {}
inconsistencies = 0


if __name__ == "__main__":
    # Check args
    if (len(sys.argv) != 2):
        sys.stderr.write("Incorrect argv \n")
        exit(1)

    # Get file
    file = sys.argv[1]
    # Open file
    try:
        inputfile = open(file, 'r')
    except IOError:
        sys.stderr.write("Could not open file \n")
        exit(1)

    # CSV reader
    cvsfile = csv.reader(inputfile)
    # Parse through csv
    for i in cvsfile:
        if i[0] == 'SUPERBLOCK':
            superblock = SUPERBLOCK(i)
        elif i[0] == 'GROUP':
            group = GROUP(i)
        elif i[0] == 'IFREE':
            Ifree.append(int(i[1]))
        elif i[0] == 'BFREE':
            Bfree.append(int(i[1]))
        elif i[0] == 'DIRENT':
            dirent.append(DIRENT(i))
        elif i[0] == 'INDIRECT':
            indirect.append(INDIRECT(i))
        elif i[0] == 'INODE':
            inode.append(INODE(i))

    min_block = group.first_block_of_inode + \
        (superblock.inodes_per_group * superblock.inode_size / superblock.block_size)
    min_block = int(min_block)

    temp_list = []
    for i in inode:
        temp_list.append(i.inode_num)
    # Do we need this???? edge case maybe idkkk , removes duplicates.
    allocated_inodes = set(temp_list)

    Block_consistency_audits()
    Inode_consistency_audits()
    Directory_consistency_audits()

    if inconsistencies == 1:
        exit(2)
    else:
        exit(0)
