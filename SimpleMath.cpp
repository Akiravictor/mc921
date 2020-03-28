#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Constants.h"
#include "llvm/Support/raw_ostream.h"
#include <string>

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
    } else if (isa<ConstantInt>(*op)) {
      ConstantInt *_V = cast<ConstantInt>(op);
      errs() << std::to_string(_V->getSExtValue()) << "\n";
    }else errs() << op << "\n";
  }

  bool runOnFunction(Function &F) {
    int i;
    for (BasicBlock &BB : F) {
      i = 0;
      for (Instruction &I : BB) {
        Value *left;
        Value *right;
        switch (I.getOpcode()) {
          case Instruction::Add:
          case Instruction::Sub:
          case Instruction::Mul:
          case Instruction::SDiv:
            left = I.getOperand(0);
            right = I.getOperand(1);
	    errs() << "I" << i << ":   " << I <<"\n";
            //errs() << "    Left operand: ";
            //printOperand(left);
            //errs() << "    Right operand: ";
            //printOperand(right);
            break;
          default:
            errs() << "I" << i << ":   " << I <<"\n";
            break;
        }
      i = i+1;
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
