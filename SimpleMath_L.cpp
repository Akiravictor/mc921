#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Constants.h"
#include "llvm/Support/raw_ostream.h"
#include <string>
#include <vector>

using namespace llvm;

namespace {
	struct SimpleMath : public FunctionPass {
		static char ID;
		SimpleMath() : FunctionPass(ID) {}

		bool doInitialization(Module &M) {
			return false;
		}

		void printOperand(Value *op) {
			if (isa<Instruction>(*op)) {
				Instruction *_I = cast<Instruction>(op);
				errs() << *_I << "\n";
			}
			else if (isa<ConstantInt>(*op)) {
				ConstantInt *_V = cast<ConstantInt>(op);
				errs() << std::to_string(_V->getSExtValue()) << "\n";
			}
			else {
				errs() << op << "\n";
			}
		}
		
		bool runOnFunction(Function &F) {
			int i;
			for (BasicBlock &BB : F) {
				i = 0;
				std::basic_string<char> left_string;
				std::basic_string<char> right_string;
				int left_int;
				int right_int;
				std::vector <Instruction*> instructions_called;
				std::vector <Instruction*> instructions_to_remove;
				std::vector <int> instructions_number;
				std::vector <int> instruction_result;
				std::vector<Instruction*>::iterator it1;
				std::vector<int>::iterator it2;
				std::vector<Instruction*>::iterator it3;
				std::vector<int>::iterator it4;
				
				for (Instruction &I : BB) {
					Value *left;
					Value *right;
					it1 = instructions_called.begin();
					it2 = instructions_number.begin();
					it3 = instructions_to_remove.begin();
					it4 = instruction_result.begin();
					
					instructions_called.push_back(&I);
					instructions_number.push_back(i);
					left = I.getOperand(0);
					right = I.getOperand(1);
					left_string = left->getName().str();
					right_string = right->getName().str();
					
					if (isa<ConstantInt>(left) && isa<ConstantInt>(right) && I.getOpcode() == Instruction::Add){
						ConstantInt *_L = cast<ConstantInt>(left);
						ConstantInt *_R = cast<ConstantInt>(right);

						int L = _L->getSExtValue();
						int R = _R->getSExtValue();
						
						int result = L + R;
						
						it3 = instructions_to_remove.insert(it3, &I);
						it4 = instruction_result.insert(it4, result);

					}
					else if (isa<ConstantInt>(left) && isa<ConstantInt>(right) && I.getOpcode() == Instruction::Sub){
						ConstantInt *_L = cast<ConstantInt>(left);
						ConstantInt *_R = cast<ConstantInt>(right);

						int L = _L->getSExtValue();
						int R = _R->getSExtValue();
						
						int result = L - R;
						
						it3 = instructions_to_remove.insert(it3, &I);
						it4 = instruction_result.insert(it4, result);

					}
					else if (isa<ConstantInt>(left) && isa<ConstantInt>(right) && I.getOpcode() == Instruction::Mul){
						ConstantInt *_L = cast<ConstantInt>(left);
						ConstantInt *_R = cast<ConstantInt>(right);

						int L = _L->getSExtValue();
						int R = _R->getSExtValue();
						
						int result = L * R;
						
						it3 = instructions_to_remove.insert(it3, &I);
						it4 = instruction_result.insert(it4, result);

					}
					else if (isa<ConstantInt>(left) && isa<ConstantInt>(right) && I.getOpcode() == Instruction::SDiv){
						ConstantInt *_L = cast<ConstantInt>(left);
						ConstantInt *_R = cast<ConstantInt>(right);

						int L = _L->getSExtValue();
						int R = _R->getSExtValue();
						
						int result = L / R;
						
						it3 = instructions_to_remove.insert(it3, &I);
						it4 = instruction_result.insert(it4, result);

					}
					
					if (left_string[0] == '.' && left_string[1] != 'i'){
						left_int = std::stoi(left_string.substr(1, left_string.size()));
						instructions_called.insert(instructions_called.begin() + left_int, &I);
						instructions_called.erase(instructions_called.begin() + left_int+1);
						instructions_number.insert(instructions_number.begin() + left_int, i);
						instructions_number.erase(instructions_number.begin() + left_int+1);
					}
					if (right_string[0] == '.' && right_string[1] != 'i'){
						right_int = std::stoi(right_string.substr(1, right_string.size()));
						instructions_called.insert(instructions_called.begin() +right_int, &I);
						instructions_called.erase(instructions_called.begin() + right_int+1);
						instructions_number.insert(instructions_number.begin() + right_int, i);
						instructions_number.erase(instructions_number.begin() + right_int+1);
					}

					i = i+1;
				}
				
				i = 0;
				
				for (Instruction &I : BB) {
				
					errs() << "I" << i << ":  " << I <<" | " << "I" << instructions_number[i] << ":  " << *instructions_called[i] << "\n";

					i = i+1;
				}
				
				for (it3 = instructions_to_remove.begin(); it3 < instructions_to_remove.end(); it3++){
					errs() << "inst: " << cast<Instruction>(*it3) << "\n";
				}
				
				for (it4 = instruction_result.begin(); it4 < instruction_result.end(); it4++){
					errs() << "result: " << *it4 << "\n";
				}
				
			}
			return false;
		}

		bool doFinalization(Module &M) {
			return false;
		}
	};
}

char SimpleMath::ID = 0;
static RegisterPass<SimpleMath> X("sm", "Simple math pass", false, false);
