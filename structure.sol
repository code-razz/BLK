//SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract studentContract{
    struct stu{
        string name;
        uint age;
        uint grade;
        uint enrollmentDate;
    }

    mapping(uint => stu) public students;

    modifier onlyExistingStudent(uint studentId) {
        require(students[studentId].enrollmentDate != 0, "Student does not exist!");
        _;
    }

    function addStudent(uint Id, string memory name, uint age,uint grade) public{
        require(students[Id].enrollmentDate==0,"Already Exist");
        students[Id]=stu(name,age,grade,block.timestamp);
    }

    function updateStudent(uint Id, uint age, uint grade) public onlyExistingStudent(Id){
        students[Id]=stu(students[Id].name,age,grade,students[Id].enrollmentDate);
    }

    function getStudent(uint Id) public view onlyExistingStudent(Id) returns(string memory,uint,uint,uint){
        return (students[Id].name,students[Id].age,students[Id].grade,students[Id].enrollmentDate);
    }

    function studentExists(uint studentId) public view returns(string memory){
        if(students[studentId].enrollmentDate==0){
            return("Does not exists");
        }else{
            return("exists");
        }
    }
}